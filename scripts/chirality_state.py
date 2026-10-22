"""Coordinated persistence for the Chirality session state.

Atomic replacement alone prevents torn JSON but not lost updates: two
writers that each load, mutate and save can silently discard one another's
change. Every read-modify-write therefore runs under an advisory lock on a
sibling lock file. Callers must not hold the lock while waiting on slow work
such as Activity startup; they do that work first and then reconcile with
``update()`` against the current state. This is concurrency control only,
not a navigation history.
"""

from __future__ import annotations

import contextlib
import fcntl
import json
import os
import tempfile
from pathlib import Path
from typing import Callable, Iterator, TypeVar

from aspartame_chirality import ChiralSession

T = TypeVar("T")


def _lock_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.lock")


@contextlib.contextmanager
def locked(path: Path) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(_lock_path(path), "a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def load(path: Path) -> ChiralSession:
    if not path.exists():
        return ChiralSession()
    return ChiralSession.from_dict(json.loads(path.read_text()))


def save(path: Path, session: ChiralSession) -> None:
    """Atomically replace the state through a unique temporary file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(session.to_dict(), stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def update(path: Path, mutate: Callable[[ChiralSession], T]) -> tuple[ChiralSession, T]:
    """Load the current state, apply ``mutate`` and save, all under the lock.

    ``mutate`` may raise to abandon the change; nothing is written then.
    """
    with locked(path):
        session = load(path)
        result = mutate(session)
        save(path, session)
        return session, result
