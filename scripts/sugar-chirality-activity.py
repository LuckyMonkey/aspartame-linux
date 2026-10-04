#!/usr/bin/env python3
"""Activate one GTK4 Activity in the single-surface Chirality adapter.

This is deliberately a small shell boundary around the presentation-independent
ChiralSession model.  It never creates panes, workspaces, geometry, or a
comparison surface.  The caller assigns two live GTK4 Activity IDs to the
semantic hands, then activates one hand at a time through the modern Sugar
Shell D-Bus contract.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path

from aspartame_chirality import ChiralSession, Hand, Side


def default_state_path() -> Path:
    runtime = os.environ.get("XDG_RUNTIME_DIR", "/tmp")
    return Path(runtime) / "aspartame" / "chirality.json"


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


def side(value: str) -> Side:
    try:
        return Side(value.lower())
    except ValueError as error:
        raise argparse.ArgumentTypeError("side must be left or right") from error


def _shell_environment() -> dict[str, str]:
    pids = subprocess.check_output(
        ["pgrep", "-u", "aspartame", "-f", "/sources/sugar/src/jarabe/main.py"],
        text=True,
    ).splitlines()
    if len(pids) != 1:
        raise RuntimeError("expected exactly one GTK4 Sugar shell")
    values = Path(f"/proc/{pids[0]}/environ").read_bytes().decode().split("\0")
    return dict(item.split("=", 1) for item in values if "=" in item)


def _activate_activity(activity_id: str) -> None:
    import dbus

    if not os.environ.get("DBUS_SESSION_BUS_ADDRESS"):
        environment = _shell_environment()
        address = environment.get("DBUS_SESSION_BUS_ADDRESS")
        if not address:
            raise RuntimeError("GTK4 shell D-Bus address is unavailable")
        os.environ["DBUS_SESSION_BUS_ADDRESS"] = address
    bus = dbus.SessionBus()
    service = f"org.laptop.Activity{activity_id}"
    if not bus.name_has_owner(service):
        raise RuntimeError(f"GTK4 Activity service is not owned: {activity_id}")
    shell = dbus.Interface(
        bus.get_object("org.laptop.Shell", "/org/laptop/Shell"),
        "org.laptop.Shell",
    )
    if not shell.ActivateActivity(activity_id):
        raise RuntimeError(f"GTK4 Shell refused Activity activation: {activity_id}")
    activity = dbus.Interface(
        bus.get_object(service, f"/org/laptop/Activity/{activity_id.replace('-', '_')}"),
        "org.laptop.Activity",
    )
    activity.SetActive(True)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument("--state-file", type=Path, default=default_state_path())
    commands = root.add_subparsers(dest="command", required=True)

    commands.add_parser("inspect")
    assign = commands.add_parser("assign")
    assign.add_argument("side", type=side)
    assign.add_argument("activity_id")
    assign.add_argument("--object-ref")
    assign.add_argument("--object-title")
    assign.add_argument("--replace", action="store_true")

    resume = commands.add_parser("resume")
    resume.add_argument("side", type=side)
    resume.add_argument("activity_id")

    activate = commands.add_parser("activate")
    activate.add_argument("side", type=side)
    release = commands.add_parser("release")
    release.add_argument("side", type=side)
    exited = commands.add_parser("activity-exited")
    exited.add_argument("activity_id")
    handoff = commands.add_parser("handoff-object")
    handoff.add_argument("source", type=side)
    handoff.add_argument("target", type=side)
    return root


def main() -> int:
    args = parser().parse_args()
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
    elif args.command == "resume":
        _activate_activity(args.activity_id)
        session.resume_activity(args.side, args.activity_id)
    elif args.command == "activate":
        hand = session.get(args.side)
        if hand is None:
            raise RuntimeError(f"{args.side.label} is empty")
        _activate_activity(hand.activity_id)
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
