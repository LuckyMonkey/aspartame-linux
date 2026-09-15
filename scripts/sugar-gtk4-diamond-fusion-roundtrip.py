#!/usr/bin/env python3
"""Guest regression: persist and resume a Diamond Fusion board."""
import json, os, subprocess, sys, time
from pathlib import Path

BUNDLE_ID = "com.francocorrea.diamondfusion"
MARKER = "diamondfusionactivity4.DiamondFusionActivity"

def wait_for(label, fn):
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        value = fn()
        if value: return value
        time.sleep(.1)
    raise RuntimeError(f"Timed out: {label}")

def main():
    if "IMAGE_ID=aspartame" not in Path("/etc/os-release").read_text(): raise SystemExit("Run in guest")
    if os.getuid() == 0:
        pids = subprocess.check_output(["pgrep", "-u", "aspartame", "-f", "/sources/sugar/src/jarabe/main.py"], text=True).splitlines()
        if len(pids) != 1: raise SystemExit("Expected one modern shell")
        env = dict(item.split("=", 1) for item in Path(f"/proc/{pids[0]}/environ").read_bytes().decode().split("\0") if "=" in item)
        interpreter = "/home/aspartame/Development/gtk4-preview/venv/bin/python"
        os.setgroups([]); os.setgid(1000); os.setuid(1000); os.execve(interpreter, [interpreter, __file__, *sys.argv[1:]], env)
    import dbus, gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi
    bus = dbus.SessionBus(); journal = dbus.Interface(bus.get_object("org.laptop.Journal", "/org/laptop/Journal"), "org.laptop.Journal")
    shell = dbus.Interface(bus.get_object("org.laptop.Shell", "/org/laptop/Shell"), "org.laptop.Shell")
    store = dbus.Interface(bus.get_object("org.laptop.sugar.DataStore", "/org/laptop/sugar/DataStore"), "org.laptop.sugar.DataStore")
    def processes():
        found = []
        for path in Path("/proc").glob("[0-9]*/cmdline"):
            try: args = path.read_bytes().decode().split("\0")
            except (OSError, UnicodeError): continue
            if MARKER in args: found.append((int(path.parent.name), args[args.index("--activity-id") + 1]))
        return found
    def find_text(node, pid, expected, depth=0):
        if depth > 12: return None
        if node.get_process_id() == pid:
            try: visible = Atspi.Text.get_text(node, 0, -1)
            except Exception: visible = ""
            try: name = node.get_name() or ""
            except Exception: name = ""
            if expected in visible or expected in name: return node
        for i in range(node.get_child_count()):
            child = node.get_child_at_index(i)
            if child is not None:
                found = find_text(child, pid, expected, depth + 1)
                if found is not None: return found
        return None
    def launch(object_id="", expected="Select two matching"):
        assert journal.LaunchBundle(BUNDLE_ID, object_id)
        pid, aid = wait_for("process", lambda: next(iter(processes()), None)); wait_for("service", lambda: bus.name_has_owner("org.laptop.Activity" + aid)); assert shell.ActivateActivity(aid)
        return pid, aid, wait_for("visible board status", lambda: find_text(Atspi.get_desktop(0), pid, expected))
    def stop(pid, aid):
        assert shell.StopActivity(aid); wait_for("exit", lambda: not Path(f"/proc/{pid}").exists()); assert not bus.name_has_owner("org.laptop.Activity" + aid); assert not shell.ActivateActivity(aid)
    if processes(): raise SystemExit("Diamond Fusion already running")
    pid, aid, node = launch(); assert "Select two matching" in Atspi.Text.get_text(node, 0, -1); stop(pid, aid)
    rows, _ = store.find(dbus.Dictionary({"activity_id": aid}, signature="sv"), dbus.Array(["uid"], signature="s")); assert len(rows) == 1
    uid = str(rows[0]["uid"]); filename = Path(str(store.get_filename(uid))); cells = [1] * 36; filename.write_text(json.dumps({"cells": cells, "score": 7}) + "\n")
    pid, aid, node = launch(uid, "Score: 7"); assert "Score: 7" in Atspi.Text.get_text(node, 0, -1); stop(pid, aid)
    assert json.loads(filename.read_text())["score"] == 7; print("diamond-fusion-roundtrip=PASS resume=PASS cleanup=PASS", flush=True)

if __name__ == "__main__": main()
