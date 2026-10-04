#!/usr/bin/env python3
"""Inspect and mutate the bounded, non-visual Chirality state.

This is a semantic milestone only.  It does not create a split screen or
replace the GTK3/GTK4 F7/F8 comparison controller.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

from aspartame_chirality import ChiralSession, Hand, Side, Spaces


def default_state_path() -> Path:
    runtime = os.environ.get("XDG_RUNTIME_DIR", "/tmp")
    return Path(runtime) / "aspartame" / "chirality.json"


def default_spaces_state_path() -> Path:
    runtime = os.environ.get("XDG_RUNTIME_DIR", "/tmp")
    return Path(runtime) / "aspartame" / "spaces.json"


def load(path: Path) -> ChiralSession:
    if not path.exists():
        return ChiralSession()
    return ChiralSession.from_dict(json.loads(path.read_text()))


def save(path: Path, session: ChiralSession) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="chirality-", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(session.to_dict(), stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_spaces(path: Path) -> Spaces:
    if not path.exists():
        return Spaces()
    return Spaces(**json.loads(path.read_text()))


def save_spaces(path: Path, spaces: Spaces) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="spaces-", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(spaces.to_dict(), stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def side(value: str) -> Side:
    try:
        return Side(value.lower())
    except ValueError as error:
        raise argparse.ArgumentTypeError("side must be left or right") from error


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument("--state-file", type=Path, default=default_state_path())
    root.add_argument("--spaces-state-file", type=Path,
                      default=default_spaces_state_path())
    commands = root.add_subparsers(dest="command", required=True)

    commands.add_parser("inspect")

    assign = commands.add_parser("assign")
    assign.add_argument("side", type=side)
    assign.add_argument("activity_id")
    assign.add_argument("--object-ref")
    assign.add_argument("--object-title")
    assign.add_argument("--replace", action="store_true")

    activate = commands.add_parser("activate")
    activate.add_argument("side", type=side)

    release = commands.add_parser("release")
    release.add_argument("side", type=side)

    exited = commands.add_parser("activity-exited")
    exited.add_argument("activity_id")

    handoff = commands.add_parser("handoff-object")
    handoff.add_argument("source", type=side)
    handoff.add_argument("target", type=side)

    commands.add_parser("spaces-inspect")
    select_space = commands.add_parser("spaces-select")
    select_space.add_argument("space_id", choices=("classic", "modern"))
    return root


def main() -> int:
    args = parser().parse_args()
    if args.command == "spaces-inspect":
        print(json.dumps(load_spaces(args.spaces_state_file).accessible_state(),
                         indent=2, sort_keys=True))
        return 0
    if args.command == "spaces-select":
        spaces = load_spaces(args.spaces_state_file)
        spaces.select(args.space_id)
        save_spaces(args.spaces_state_file, spaces)
        print(json.dumps(spaces.accessible_state(), indent=2, sort_keys=True))
        return 0
    session = load(args.state_file)
    if args.command == "inspect":
        print(json.dumps(session.accessible_state(), indent=2, sort_keys=True))
        return 0
    if args.command == "assign":
        session.assign(
            args.side,
            Hand(args.activity_id, args.object_ref, args.object_title),
            replace=args.replace,
        )
    elif args.command == "activate":
        session.activate(args.side)
    elif args.command == "release":
        session.release(args.side)
    elif args.command == "activity-exited":
        session.activity_exited(args.activity_id)
    elif args.command == "handoff-object":
        session.handoff_object(args.source, args.target)
    save(args.state_file, session)
    print(json.dumps(session.accessible_state(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
