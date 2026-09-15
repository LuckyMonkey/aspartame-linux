#!/usr/bin/env python3
"""Guest regression: persist and resume a Get Things Done task list."""

import json
import os
from pathlib import Path
import subprocess
import sys
import time

BUNDLE_ID = "org.sugarlabs.GTDActivity"
PROCESS_MARKER = "gtdactivity4.GTDActivity"


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
        env = dict(item.split("=", 1) for item in Path(f"/proc/{pids[0]}/environ").read_bytes().decode().split("\0") if "=" in item)
        interpreter = "/home/aspartame/Development/gtk4-preview/venv/bin/python"
        os.setgroups([]); os.setgid(1000); os.setuid(1000)
        os.execve(interpreter, [interpreter, __file__, *sys.argv[1:]], env)

    import dbus
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    bus = dbus.SessionBus()
    journal = dbus.Interface(bus.get_object("org.laptop.Journal", "/org/laptop/Journal"), "org.laptop.Journal")
    shell = dbus.Interface(bus.get_object("org.laptop.Shell", "/org/laptop/Shell"), "org.laptop.Shell")
    store = dbus.Interface(bus.get_object("org.laptop.sugar.DataStore", "/org/laptop/sugar/DataStore"), "org.laptop.sugar.DataStore")

    def processes():
        result = []
        for path in Path("/proc").glob("[0-9]*/cmdline"):
            try: args = path.read_bytes().decode().split("\0")
            except (FileNotFoundError, PermissionError, ProcessLookupError): continue
            if PROCESS_MARKER in args:
                result.append((int(path.parent.name), args[args.index("--activity-id") + 1]))
        return result

    def find_text(node, pid, expected, depth=0):
        if depth > 12: return None
        if node.get_process_id() == pid:
            try: visible = Atspi.Text.get_text(node, 0, -1)
            except Exception: visible = ""
            if expected in visible: return node
        for i in range(node.get_child_count()):
            child = node.get_child_at_index(i)
            if child is not None:
                found = find_text(child, pid, expected, depth + 1)
                if found is not None: return found
        return None

    def launch(object_id="", expected="0 tasks"):
        assert journal.LaunchBundle(BUNDLE_ID, object_id)
        pid, activity_id = wait_for("GTD process", lambda: next(iter(processes()), None))
        wait_for("Activity service", lambda: bus.name_has_owner("org.laptop.Activity" + activity_id))
        wait_for("shell launch completion", lambda: shell.ActivateActivity(activity_id))
        node = wait_for("visible task summary", lambda: find_text(Atspi.get_desktop(0), pid, expected))
        return pid, activity_id, node

    def stop(pid, activity_id):
        assert shell.StopActivity(activity_id)
        wait_for("process exit", lambda: not Path(f"/proc/{pid}").exists())
        assert not bus.name_has_owner("org.laptop.Activity" + activity_id)
        assert not shell.ActivateActivity(activity_id), "stale shell activity"

    if processes(): raise SystemExit("GTD is already running; stop it before this probe.")
    cycles = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    for cycle in range(1, cycles + 1):
        pid, activity_id, node = launch()
        assert Atspi.Text.get_text(node, 0, -1) == "0 tasks"
        stop(pid, activity_id)
        rows, _ = store.find(dbus.Dictionary({"activity_id": activity_id}, signature="sv"), dbus.Array(["uid"], signature="s"))
        assert len(rows) == 1, "expected one saved GTD Journal object"
        uid = str(rows[0]["uid"]); filename = Path(str(store.get_filename(uid)))
        filename.write_text(json.dumps({"tasks": [{"text": "Call the team", "done": False}, {"text": "Ship GTK4", "done": True}]}) + "\n", encoding="utf-8")
        resumed_pid, resumed_id, resumed = launch(uid, "2 tasks")
        assert Atspi.Text.get_text(resumed, 0, -1) == "2 tasks · 1 complete"
        stop(resumed_pid, resumed_id)
        assert json.loads(filename.read_text(encoding="utf-8"))["tasks"][1]["done"] is True
        print(f"cycle={cycle} pid={pid} resumed_pid={resumed_pid} object={uid} resume=PASS service-release=PASS shell-cleanup=PASS", flush=True)
    print("gtd-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded", flush=True)


if __name__ == "__main__": main()
