#!/usr/bin/env python3
"""Guest regression: resume a Read Journal object and verify visible text.

This exercises real Read Activity processes and the Journal object path. The
test seeds the datastore backing file directly after Read creates its object;
that keeps the probe focused on Read resume/render behavior rather than a file
picker or import workflow. Run as root inside the development VM.
"""

import os
from pathlib import Path
import subprocess
import sys
import time


BUNDLE_ID = "org.laptop.sugar.ReadActivity"
PROCESS_MARKER = "readactivity4.ReadActivity"


def wait_for(description, callback):
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        result = callback()
        if result:
            return result
        time.sleep(0.1)
    raise RuntimeError(f"Timed out: {description}")


def main():
    if "IMAGE_ID=aspartame" not in Path("/etc/os-release").read_text():
        raise SystemExit("Run this probe inside the Aspartame guest.")
    if os.getuid() == 0:
        pids = subprocess.check_output(
            ["pgrep", "-u", "aspartame", "-f", "/sources/sugar/src/jarabe/main.py"],
            text=True,
        ).splitlines()
        if len(pids) != 1:
            raise SystemExit("Expected exactly one modern shell.")
        env = dict(
            item.split("=", 1)
            for item in Path(f"/proc/{pids[0]}/environ").read_bytes().decode().split("\0")
            if "=" in item
        )
        interpreter = "/home/aspartame/Development/gtk4-preview/venv/bin/python"
        os.setgroups([])
        os.setgid(1000)
        os.setuid(1000)
        os.execve(interpreter, [interpreter, __file__, *sys.argv[1:]], env)

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
        result = []
        for path in Path("/proc").glob("[0-9]*/cmdline"):
            try:
                args = path.read_bytes().decode().split("\0")
            except (FileNotFoundError, PermissionError, ProcessLookupError):
                continue
            if PROCESS_MARKER in args:
                result.append((int(path.parent.name), args[args.index("--activity-id") + 1]))
        return result

    def find_document(node, pid, expected_text, depth=0):
        if depth > 12:
            return None
        if node.get_process_id() == pid:
            try:
                visible_text = Atspi.Text.get_text(node, 0, -1)
            except Exception:
                visible_text = ""
            if expected_text in visible_text:
                return node
        for i in range(node.get_child_count()):
            child = node.get_child_at_index(i)
            if child is not None:
                found = find_document(child, pid, expected_text, depth + 1)
                if found is not None:
                    return found
        return None

    def launch(object_id="", expected_text="Welcome to Read"):
        assert journal.LaunchBundle(BUNDLE_ID, object_id)
        pid, activity_id = wait_for("Read process", lambda: next(iter(processes()), None))
        wait_for("Activity service", lambda: bus.name_has_owner("org.laptop.Activity" + activity_id))
        wait_for("shell launch completion", lambda: shell.ActivateActivity(activity_id))
        document = wait_for(
            "visible Read text",
            lambda: find_document(Atspi.get_desktop(0), pid, expected_text),
        )
        return pid, activity_id, document

    def stop(pid, activity_id):
        assert shell.StopActivity(activity_id)
        wait_for("process exit", lambda: not Path(f"/proc/{pid}").exists())
        assert not bus.name_has_owner("org.laptop.Activity" + activity_id)
        assert not shell.ActivateActivity(activity_id), "stale shell activity"

    if processes():
        raise SystemExit("Read is already running; stop it before this probe.")
    cycles = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    if cycles < 1:
        raise SystemExit("cycles must be positive")

    for cycle in range(1, cycles + 1):
        payload = (
            f"Aspartame Read round trip {cycle}: cafe resume proof\n"
            "Visible page one.\fVisible page two."
        )
        pid, activity_id, document = launch()
        assert "Welcome to Read" in Atspi.Text.get_text(document, 0, -1)
        stop(pid, activity_id)
        rows, _ = store.find(
            dbus.Dictionary({"activity_id": activity_id}, signature="sv"),
            dbus.Array(["uid"], signature="s"),
        )
        assert len(rows) == 1, "expected one saved Read Journal object"
        uid = str(rows[0]["uid"])
        filename = Path(str(store.get_filename(uid)))
        filename.write_text(payload, encoding="utf-8")

        expected_page = payload.split("\f")[0]
        resumed_pid, resumed_id, resumed = launch(uid, expected_page)
        assert resumed_pid != pid
        assert Atspi.Text.get_text(resumed, 0, -1) == expected_page
        stop(resumed_pid, resumed_id)
        assert filename.read_text(encoding="utf-8") == payload
        print(
            f"cycle={cycle} pid={pid} resumed_pid={resumed_pid} object={uid} "
            "resume=PASS service-release=PASS shell-cleanup=PASS",
            flush=True,
        )
    print("read-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded", flush=True)


if __name__ == "__main__":
    main()
