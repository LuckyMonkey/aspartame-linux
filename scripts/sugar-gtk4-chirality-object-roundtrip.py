#!/usr/bin/env python3
"""Qualify one UTF-8 Journal object across two GTK4 Chirality hands.

The probe deliberately uses ordinary Journal launches and the semantic
Chirality adapter.  It does not create panes or a second display surface:
Write and Read are two Activity clients of one Journal UID, and only one is
activated at a time.
"""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parent
ADAPTER = ROOT / "sugar-chirality-activity.py"
WRITE_BUNDLE = "org.sugarlabs.Write"
WRITE_MARKER = "writeactivity4.WriteActivity"
READ_BUNDLE = "org.laptop.sugar.ReadActivity"
READ_MARKER = "readactivity4.ReadActivity"


def wait_for(description, callback):
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        value = callback()
        if value:
            return value
        time.sleep(0.1)
    raise RuntimeError(f"timed out waiting for {description}")


def reexec_as_desktop_user():
    if os.getuid() != 0:
        return
    shells = subprocess.check_output(
        ["pgrep", "-u", "aspartame", "-f", "/sources/sugar/src/jarabe/main.py"],
        text=True,
    ).splitlines()
    if len(shells) != 1:
        raise RuntimeError("expected exactly one modern shell")
    environment = dict(
        item.split("=", 1)
        for item in Path(f"/proc/{shells[0]}/environ").read_bytes()
        .decode()
        .split("\0")
        if "=" in item
    )
    python = os.environ.get(
        "GTK4_PYTHON", "/usr/lib/aspartame/gtk4-preview/venv/bin/python"
    )
    os.setgroups([])
    os.setgid(1000)
    os.setuid(1000)
    os.execve(python, [python, __file__], environment)


def main():
    reexec_as_desktop_user()
    import dbus
    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    bus = dbus.SessionBus()
    journal = dbus.Interface(
        bus.get_object("org.laptop.Journal", "/org/laptop/Journal"),
        "org.laptop.Journal",
    )
    shell = dbus.Interface(
        bus.get_object("org.laptop.Shell", "/org/laptop/Shell"),
        "org.laptop.Shell",
    )
    store = dbus.Interface(
        bus.get_object("org.laptop.sugar.DataStore", "/org/laptop/sugar/DataStore"),
        "org.laptop.sugar.DataStore",
    )

    def processes(marker):
        found = []
        for command_path in Path("/proc").glob("[0-9]*/cmdline"):
            try:
                args = command_path.read_bytes().decode().split("\0")
            except (FileNotFoundError, PermissionError, ProcessLookupError):
                continue
            if marker not in args or "--activity-id" not in args:
                continue
            object_id = ""
            if "--object-id" in args:
                index = args.index("--object-id") + 1
                if index < len(args):
                    object_id = args[index]
            found.append(
                {
                    "pid": int(command_path.parent.name),
                    "activity_id": args[args.index("--activity-id") + 1],
                    "object_id": object_id,
                }
            )
        return found

    def find_text(node, pid, expected=None, name=None, depth=0):
        if depth > 14:
            return None
        if node.get_process_id() == pid:
            if name is None or node.get_name() == name:
                try:
                    visible = Atspi.Text.get_text(node, 0, -1)
                except Exception:
                    visible = ""
                if expected is None or expected in visible:
                    return node
        for index in range(node.get_child_count()):
            child = node.get_child_at_index(index)
            if child is not None:
                found = find_text(child, pid, expected, name, depth + 1)
                if found is not None:
                    return found
        return None

    def launch(bundle, marker, object_id="", expected=None, name=None):
        if not journal.LaunchBundle(bundle, object_id):
            raise RuntimeError(f"Journal refused {bundle}")
        process = wait_for(
            f"{bundle} process",
            lambda: next(
                (
                    item
                    for item in processes(marker)
                    if item["object_id"] == object_id
                ),
                None,
            ),
        )
        activity_id = process["activity_id"]
        wait_for(
            f"{bundle} service",
            lambda: bus.name_has_owner(f"org.laptop.Activity{activity_id}"),
        )
        if not shell.ActivateActivity(activity_id):
            raise RuntimeError(f"Shell refused {activity_id}")
        document = wait_for(
            f"{bundle} visible document",
            lambda: find_text(
                Atspi.get_desktop(0),
                process["pid"],
                expected,
                name,
            ),
        )
        return process["pid"], activity_id, document

    def stop(pid, activity_id):
        if not Path(f"/proc/{pid}").exists():
            return
        if not shell.StopActivity(activity_id):
            raise RuntimeError(f"Shell refused stop for {activity_id}")
        wait_for(f"cleanup {activity_id}", lambda: not Path(f"/proc/{pid}").exists())
        if bus.name_has_owner(f"org.laptop.Activity{activity_id}"):
            raise RuntimeError(f"Activity service remained owned: {activity_id}")
        if shell.ActivateActivity(activity_id):
            raise RuntimeError(f"stale shell Activity: {activity_id}")

    def run_adapter(state, *args):
        result = subprocess.run(
            [sys.executable, str(ADAPTER), "--state-file", str(state), *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)

    if processes(WRITE_MARKER) or processes(READ_MARKER):
        raise SystemExit("Write or Read is already running; stop it before this probe.")

    content = "Aspartame Chirality object: café — one real UTF-8 Journal payload."
    live = []
    with tempfile.TemporaryDirectory(prefix="chirality-object-") as directory:
        state = Path(directory) / "chirality.json"
        try:
            pid, activity_id, document = launch(
                WRITE_BUNDLE, WRITE_MARKER, name="Document text"
            )
            live.append((pid, activity_id))
            assert Atspi.EditableText.set_text_contents(document, content)
            assert Atspi.Text.get_text(document, 0, -1) == content
            stop(pid, activity_id)
            live.remove((pid, activity_id))

            rows, _ = store.find(
                dbus.Dictionary({"activity_id": activity_id}, signature="sv"),
                dbus.Array(["uid"], signature="s"),
            )
            if len(rows) != 1:
                raise RuntimeError("expected exactly one saved Journal object")
            uid = str(rows[0]["uid"])
            filename = Path(str(store.get_filename(uid)))
            if filename.read_text(encoding="utf-8") != content:
                raise RuntimeError("initial Journal payload differs")

            write = launch(WRITE_BUNDLE, WRITE_MARKER, uid, expected=content)
            live.append(write[:2])
            run_adapter(
                state,
                "assign",
                "left",
                write[1],
                "--object-ref",
                uid,
                "--object-title",
                "UTF-8 Chirality object",
                "--bundle-id",
                WRITE_BUNDLE,
            )
            left = run_adapter(state, "activate", "left")
            assert left["active_hand"] == "left"

            read = launch(READ_BUNDLE, READ_MARKER, uid, expected=content)
            live.append(read[:2])
            run_adapter(
                state, "assign", "right", read[1],
                "--bundle-id", READ_BUNDLE,
            )
            handed = run_adapter(state, "handoff-object", "left", "right")
            assert handed["hands"][0]["object_ref"] == uid
            assert handed["hands"][1]["object_ref"] == uid

            right = run_adapter(state, "activate", "right")
            assert right["active_hand"] == "right"
            left_again = run_adapter(state, "activate", "left")
            assert left_again["active_hand"] == "left"
            assert left_again["hands"][0]["object_ref"] == uid
            assert left_again["hands"][1]["object_ref"] == uid

            stop(*read[:2])
            live.remove(read[:2])
            after_read = run_adapter(state, "activity-exited", read[1])
            assert after_read["active_hand"] == "left"
            assert after_read["hands"][1]["activity_id"] is None

            stop(*write[:2])
            live.remove(write[:2])
            finished = run_adapter(state, "activity-exited", write[1])
            assert finished["active_hand"] is None
            assert all(hand["activity_id"] is None for hand in finished["hands"])
            if filename.read_text(encoding="utf-8") != content:
                raise RuntimeError("Journal payload changed during handoff")

            print(
                "chirality-object-roundtrip=PASS "
                f"object={uid} active-sequence=left,right,left "
                "hands=write,read payload=utf8 cleanup=PASS mode=single-surface",
                flush=True,
            )
        finally:
            for pid, activity_id in reversed(live):
                try:
                    stop(pid, activity_id)
                except Exception:
                    pass


if __name__ == "__main__":
    main()
