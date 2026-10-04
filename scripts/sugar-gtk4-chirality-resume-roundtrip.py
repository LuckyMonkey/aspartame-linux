#!/usr/bin/env python3
"""Qualify replacing a GTK4 Activity while retaining its Journal object."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parent
ADAPTER = ROOT / "sugar-chirality-activity.py"
BUNDLE = "org.sugarlabs.Write"
MARKER = "writeactivity4.WriteActivity"


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

    def processes():
        found = []
        for command_path in Path("/proc").glob("[0-9]*/cmdline"):
            try:
                args = command_path.read_bytes().decode().split("\0")
            except (FileNotFoundError, PermissionError, ProcessLookupError):
                continue
            if MARKER not in args or "--activity-id" not in args:
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

    def find_document(node, pid, expected, depth=0):
        if depth > 14:
            return None
        if node.get_process_id() == pid:
            if expected is None and node.get_name() == "Document text":
                return node
            try:
                visible = Atspi.Text.get_text(node, 0, -1)
            except Exception:
                visible = ""
            if expected is not None and expected in visible:
                return node
        for index in range(node.get_child_count()):
            child = node.get_child_at_index(index)
            if child is not None:
                found = find_document(child, pid, expected, depth + 1)
                if found is not None:
                    return found
        return None

    def launch(object_id="", expected=None):
        if not journal.LaunchBundle(BUNDLE, object_id):
            raise RuntimeError("Journal refused Write")
        process = wait_for(
            "Write process",
            lambda: next(
                (item for item in processes() if item["object_id"] == object_id),
                None,
            ),
        )
        activity_id = process["activity_id"]
        wait_for(
            "Write service",
            lambda: bus.name_has_owner(f"org.laptop.Activity{activity_id}"),
        )
        if not shell.ActivateActivity(activity_id):
            raise RuntimeError(f"Shell refused {activity_id}")
        try:
            document = wait_for(
                "Write document",
                lambda: find_document(
                    Atspi.get_desktop(0), process["pid"], expected
                ),
            )
        except Exception:
            # The process was discovered before the accessibility tree became
            # ready; do not leave a failed qualification client behind.
            try:
                shell.StopActivity(activity_id)
            except Exception:
                pass
            raise
        return process["pid"], activity_id, document

    def stop(pid, activity_id):
        if not Path(f"/proc/{pid}").exists():
            return
        if not shell.StopActivity(activity_id):
            raise RuntimeError(f"Shell refused stop for {activity_id}")
        wait_for(f"cleanup {activity_id}", lambda: not Path(f"/proc/{pid}").exists())
        if bus.name_has_owner(f"org.laptop.Activity{activity_id}"):
            raise RuntimeError(f"Activity service remained owned: {activity_id}")

    def run_adapter(state, *args):
        result = subprocess.run(
            [sys.executable, str(ADAPTER), "--state-file", str(state), *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)

    if processes():
        raise SystemExit("Write is already running; stop it before this probe.")

    content = "Aspartame Chirality resume: café — the same Journal object."
    live = []
    with tempfile.TemporaryDirectory(prefix="chirality-resume-") as directory:
        state = Path(directory) / "chirality.json"
        try:
            created = launch()
            live.append(created[:2])
            assert Atspi.EditableText.set_text_contents(created[2], content)
            assert Atspi.Text.get_text(created[2], 0, -1) == content
            stop(*created[:2])
            live.remove(created[:2])

            rows, _ = store.find(
                dbus.Dictionary({"activity_id": created[1]}, signature="sv"),
                dbus.Array(["uid"], signature="s"),
            )
            if len(rows) != 1:
                raise RuntimeError("expected one saved Journal object")
            uid = str(rows[0]["uid"])
            filename = Path(str(store.get_filename(uid)))
            if filename.read_text(encoding="utf-8") != content:
                raise RuntimeError("initial Journal payload differs")

            original = launch(uid, content)
            live.append(original[:2])
            run_adapter(
                state,
                "assign",
                "left",
                original[1],
                "--object-ref",
                uid,
                "--object-title",
                "UTF-8 resume object",
            )
            active = run_adapter(state, "activate", "left")
            assert active["active_hand"] == "left"

            # Leave the persisted hand record in place while the Activity
            # client disappears.  The resume command must replace only its
            # Activity ID and retain the object reference.
            stop(*original[:2])
            live.remove(original[:2])
            replacement = launch(uid, content)
            live.append(replacement[:2])
            resumed = run_adapter(state, "resume", "left", replacement[1])
            assert resumed["active_hand"] == "left"
            assert resumed["hands"][0]["activity_id"] == replacement[1]
            assert resumed["hands"][0]["object_ref"] == uid
            assert Atspi.Text.get_text(replacement[2], 0, -1) == content

            stop(*replacement[:2])
            live.remove(replacement[:2])
            finished = run_adapter(state, "activity-exited", replacement[1])
            assert finished["active_hand"] is None
            assert all(hand["activity_id"] is None for hand in finished["hands"])
            if filename.read_text(encoding="utf-8") != content:
                raise RuntimeError("Journal payload changed during resume")
            print(
                "chirality-resume-roundtrip=PASS "
                f"object={uid} active=left replacement={replacement[1]} "
                "payload=utf8 state-clean=PASS mode=single-surface",
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
