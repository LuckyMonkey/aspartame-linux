#!/usr/bin/env python3
"""Guest regression: restore a Calculate expression from the Journal."""
import os, subprocess, sys, time
from pathlib import Path

BUNDLE_ID = "org.aspartame.Calculate"
PROCESS_MARKER = "calculateactivity4.CalculateActivity"

def wait_for(description, callback):
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        result = callback()
        if result: return result
        time.sleep(0.1)
    raise RuntimeError(f"Timed out: {description}")

def main():
    if "IMAGE_ID=aspartame" not in Path("/etc/os-release").read_text(): raise SystemExit("Run inside Aspartame guest")
    if os.getuid() == 0:
        shells = subprocess.check_output(["pgrep", "-u", "aspartame", "-f", "/sources/sugar/src/jarabe/main.py"], text=True).splitlines()
        if len(shells) != 1: raise SystemExit("Expected exactly one modern shell")
        env = dict(item.split("=", 1) for item in Path(f"/proc/{shells[0]}/environ").read_bytes().decode().split("\0") if "=" in item)
        interpreter = "/home/aspartame/Development/gtk4-preview/venv/bin/python"
        os.setgroups([]); os.setgid(1000); os.setuid(1000); os.execve(interpreter, [interpreter, __file__, *sys.argv[1:]], env)
    import dbus, gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi
    bus = dbus.SessionBus()
    journal = dbus.Interface(bus.get_object("org.laptop.Journal", "/org/laptop/Journal"), "org.laptop.Journal")
    shell = dbus.Interface(bus.get_object("org.laptop.Shell", "/org/laptop/Shell"), "org.laptop.Shell")
    store = dbus.Interface(bus.get_object("org.laptop.sugar.DataStore", "/org/laptop/sugar/DataStore"), "org.laptop.sugar.DataStore")
    def processes():
        found = []
        for path in Path("/proc").glob("[0-9]*/cmdline"):
            try: args = path.read_bytes().decode().split("\0")
            except (FileNotFoundError, PermissionError, ProcessLookupError): continue
            if PROCESS_MARKER in args: found.append((int(path.parent.name), args[args.index("--activity-id") + 1]))
        return found
    def find_text(node, pid, expected, depth=0):
        if depth > 12: return None
        if node.get_process_id() == pid:
            try: visible = Atspi.Text.get_text(node, 0, -1)
            except Exception: visible = ""
            if expected in visible: return node
        for i in range(node.get_child_count()):
            child = node.get_child_at_index(i)
            if child is not None:
                result = find_text(child, pid, expected, depth + 1)
                if result is not None: return result
        return None
    def has_text(node, pid, expected, depth=0):
        return find_text(node, pid, expected, depth) is not None

    def launch(object_id="", expected="Calculate"):
        assert journal.LaunchBundle(BUNDLE_ID, object_id)
        pid, aid = wait_for("Calculate process", lambda: next(iter(processes()), None))
        wait_for("Activity service", lambda: bus.name_has_owner("org.laptop.Activity" + aid))
        wait_for("shell launch", lambda: shell.ActivateActivity(aid))
        return pid, aid, wait_for("visible calculator", lambda: find_text(Atspi.get_desktop(0), pid, expected))
    def stop(pid, aid):
        assert shell.StopActivity(aid); wait_for("process exit", lambda: not Path(f"/proc/{pid}").exists())
        assert not bus.name_has_owner("org.laptop.Activity" + aid); assert not shell.ActivateActivity(aid)
    if processes(): raise SystemExit("Calculate already running")
    cycles = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    for cycle in range(1, cycles + 1):
        pid, aid, node = launch(); stop(pid, aid)
        rows, _ = store.find(dbus.Dictionary({"activity_id": aid}, signature="sv"), dbus.Array(["uid"], signature="s"))
        assert len(rows) == 1, "expected Calculate Journal object"
        uid = str(rows[0]["uid"]); filename = Path(str(store.get_filename(uid))); filename.write_text("7 * 6\n", encoding="utf-8")
        resumed_pid, resumed_aid, resumed = launch(uid, "7 * 6")
        desktop = Atspi.get_desktop(0)
        assert has_text(desktop, resumed_pid, "42")
        stop(resumed_pid, resumed_aid)
        assert filename.read_text(encoding="utf-8").strip() == "7 * 6"
        print(f"cycle={cycle} pid={pid} resumed_pid={resumed_pid} object={uid} resume=PASS service-release=PASS shell-cleanup=PASS", flush=True)
    print("calculate-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded", flush=True)

if __name__ == "__main__": main()
