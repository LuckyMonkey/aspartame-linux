#!/usr/bin/env python3
"""Guest regression: resume Reversi board/player state from Journal."""
import json, os, subprocess, sys, time
from pathlib import Path
BUNDLE_ID = "net.coderanger.olpc.reversi"; MARKER = "reversiactivity4.ReversiActivity"
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
        interpreter = "/home/aspartame/Development/gtk4-preview/venv/bin/python"; os.setgroups([]); os.setgid(1000); os.setuid(1000); os.execve(interpreter, [interpreter, __file__, *sys.argv[1:]], env)
    import dbus, gi; gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi
    bus = dbus.SessionBus(); journal = dbus.Interface(bus.get_object("org.laptop.Journal", "/org/laptop/Journal"), "org.laptop.Journal"); shell = dbus.Interface(bus.get_object("org.laptop.Shell", "/org/laptop/Shell"), "org.laptop.Shell"); store = dbus.Interface(bus.get_object("org.laptop.sugar.DataStore", "/org/laptop/sugar/DataStore"), "org.laptop.sugar.DataStore")
    def procs():
        found = []
        for path in Path("/proc").glob("[0-9]*/cmdline"):
            try: args = path.read_bytes().decode().split("\0")
            except OSError: continue
            if MARKER in args: found.append((int(path.parent.name), args[args.index("--activity-id") + 1]))
        return found
    def find(node, pid, expected, depth=0):
        if depth > 12: return None
        if node.get_process_id() == pid:
            try: text = Atspi.Text.get_text(node, 0, -1)
            except Exception: text = ""
            if expected in text: return node
        for i in range(node.get_child_count()):
            child = node.get_child_at_index(i)
            if child is not None:
                result = find(child, pid, expected, depth + 1)
                if result is not None: return result
        return None
    def launch(uid=""):
        assert journal.LaunchBundle(BUNDLE_ID, uid); pid, aid = wait_for("process", lambda: next(iter(procs()), None)); wait_for("service", lambda: bus.name_has_owner("org.laptop.Activity" + aid)); assert shell.ActivateActivity(aid); return pid, aid, wait_for("visible Reversi", lambda: find(Atspi.get_desktop(0), pid, "Reversi"))
    def stop(pid, aid):
        assert shell.StopActivity(aid); wait_for("exit", lambda: not Path(f"/proc/{pid}").exists()); assert not bus.name_has_owner("org.laptop.Activity" + aid); assert not shell.ActivateActivity(aid)
    pid, aid, node = launch(); stop(pid, aid)
    rows, _ = store.find(dbus.Dictionary({"activity_id": aid}, signature="sv"), dbus.Array(["uid"], signature="s")); assert len(rows) == 1
    uid = str(rows[0]["uid"]); filename = Path(str(store.get_filename(uid))); board = [[0] * 8 for _ in range(8)]; board[0][0] = board[0][1] = board[1][0] = board[3][3] = board[4][4] = 1; board[3][4] = board[4][3] = 2
    filename.write_text(json.dumps({"board": board, "player": 2}) + "\n")
    pid, aid, node = launch(uid); count_node = wait_for("restored score", lambda: find(Atspi.get_desktop(0), pid, "Black 5")); assert "Black 5" in Atspi.Text.get_text(count_node, 0, -1); stop(pid, aid)
    print("reversi-roundtrip=PASS resume=PASS cleanup=PASS", flush=True)
if __name__ == "__main__": main()
