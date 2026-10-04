#!/usr/bin/env python3
"""Rehydrate persisted GTK4 Chirality hands after a modern shell restart.

The state file contains only the two current hand descriptors.  Activity IDs
are process-local, so this helper launches each declared GTK4 bundle again,
replaces the stale ID, and restores the one active hand.  It never records a
previous hand, frame, or launch event.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parent
sys_path = str(ROOT)
if sys_path not in sys.path:
    sys.path.insert(0, sys_path)

from aspartame_chirality import ChiralSession, Side  # noqa: E402


def default_state_path() -> Path:
    configured = os.environ.get("ASPARTAME_CHIRALITY_STATE_FILE")
    if configured:
        return Path(configured)
    state_home = os.environ.get(
        "XDG_STATE_HOME", str(Path.home() / ".local" / "state")
    )
    return Path(state_home) / "aspartame" / "chirality.json"


def wait_for(description, callback, timeout=30):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = callback()
        if value:
            return value
        time.sleep(0.1)
    raise RuntimeError(f"timed out waiting for {description}")


def load(path: Path) -> ChiralSession:
    return ChiralSession.from_dict(json.loads(path.read_text()))


def save(path: Path, session: ChiralSession) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.resume-tmp")
    temporary.write_text(
        json.dumps(session.to_dict(), indent=2, sort_keys=True) + "\n"
    )
    os.replace(temporary, path)


def process_environment(pid: int) -> dict[str, str]:
    try:
        values = Path(f"/proc/{pid}/environ").read_bytes().decode().split("\0")
    except (FileNotFoundError, PermissionError, ProcessLookupError):
        return {}
    return dict(item.split("=", 1) for item in values if "=" in item)


def activity_processes(bundle_id: str, object_ref: str | None, ignored: set[int]):
    found = []
    for command_path in Path("/proc").glob("[0-9]*/cmdline"):
        try:
            pid = int(command_path.parent.name)
        except ValueError:
            continue
        if pid in ignored:
            continue
        environment = process_environment(pid)
        if environment.get("SUGAR_BUNDLE_ID") != bundle_id:
            continue
        if object_ref and environment.get("SUGAR_OBJECT_ID") != object_ref:
            continue
        activity_id = environment.get("SUGAR_ACTIVITY_ID")
        if activity_id:
            found.append((pid, activity_id))
    return found


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument("--state-file", type=Path, default=default_state_path())
    return root


def main() -> int:
    args = parser().parse_args()
    if not args.state_file.exists():
        print("chirality-resume=IDLE reason=no-state", flush=True)
        return 0

    import dbus

    bus = dbus.SessionBus()
    wait_for("GTK4 Shell D-Bus service", lambda: bus.name_has_owner("org.laptop.Shell"))
    wait_for(
        "GTK4 Journal D-Bus service",
        lambda: bus.name_has_owner("org.laptop.Journal"),
    )
    journal = dbus.Interface(
        bus.get_object("org.laptop.Journal", "/org/laptop/Journal"),
        "org.laptop.Journal",
    )
    shell = dbus.Interface(
        bus.get_object("org.laptop.Shell", "/org/laptop/Shell"),
        "org.laptop.Shell",
    )
    session = load(args.state_file)
    restored = []
    skipped = []

    for side in (Side.LEFT, Side.RIGHT):
        hand = session.get(side)
        if hand is None:
            continue
        if not hand.bundle_id:
            skipped.append(f"{side.value}:missing-bundle")
            continue
        before = {
            int(path.parent.name)
            for path in Path("/proc").glob("[0-9]*/cmdline")
            if path.parent.name.isdigit()
        }
        object_id = hand.object_ref or ""
        if not journal.LaunchBundle(hand.bundle_id, object_id):
            raise RuntimeError(
                f"Journal refused {side.value} hand: {hand.bundle_id}"
            )
        process = wait_for(
            f"{side.value} {hand.bundle_id} Activity",
            lambda: next(
                iter(activity_processes(hand.bundle_id, hand.object_ref, before)),
                None,
            ),
        )
        _pid, activity_id = process
        wait_for(
            f"{side.value} Activity service",
            lambda: bus.name_has_owner(f"org.laptop.Activity{activity_id}"),
        )
        session.resume_activity(side, activity_id, hand.bundle_id)
        save(args.state_file, session)
        restored.append(f"{side.value}:{activity_id}")

    active = session.active_hand
    if active is not None:
        hand = session.get(active)
        if hand is not None and hand.activity_id in {
            value.split(":", 1)[1] for value in restored
        }:
            if not shell.ActivateActivity(hand.activity_id):
                raise RuntimeError(f"Shell refused active hand: {active.value}")

    print(
        "chirality-resume=PASS "
        f"restored={','.join(restored) or 'none'} "
        f"skipped={','.join(skipped) or 'none'} "
        "mode=single-surface history=none",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
