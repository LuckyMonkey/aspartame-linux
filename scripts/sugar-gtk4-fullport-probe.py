#!/usr/bin/env python3
"""Guest half of the FULL PORT receipt: observe a GTK4 Activity over AT-SPI.

The host driver (sugar-gtk4-fullport-receipt.py) delivers real keyboard
input through QEMU and calls these subcommands between keystrokes:

  launch BUNDLE_ID MARKER [UID]  start (or resume) an Activity; JSON pid/aid
  focused PID                    accessible name and role of the focused node
  text PID NAME                  text of the node with that accessible name
  stop PID AID [UID]             stop it; JSON Journal uid and payload path
                                 (pass UID when resuming: the object keeps its
                                 original activity_id)
  a11y PID                       interactive nodes that have no accessible name
  names PID                      every node: role, name and text (for writing specs)
  payload UID                    payload path of a Journal object
"""
import json, os, subprocess, sys, time
from pathlib import Path

INTERACTIVE = {"button", "push button", "toggle button", "check box", "radio button",
               "combo box", "entry", "text", "spin button", "slider", "link"}


def reexec_as_session_user():
    shells = subprocess.check_output(
        ["pgrep", "-u", "aspartame", "-f", "/sources/sugar/src/jarabe/main.py"],
        text=True).split()
    if len(shells) != 1:
        raise SystemExit("expected one modern shell, found %d" % len(shells))
    env = dict(item.split("=", 1) for item in
               Path("/proc/%s/environ" % shells[0]).read_bytes().decode().split("\0")
               if "=" in item)
    py = next(c for c in ("/usr/lib/aspartame/gtk4-preview/venv/bin/python",
                          "/home/aspartame/Development/gtk4-preview/venv/bin/python")
              if Path(c).exists())
    os.setgroups([]); os.setgid(1000); os.setuid(1000)
    os.execve(py, [py, __file__, *sys.argv[1:]], env)


def wait_for(desc, fn, timeout=20):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        value = fn()
        if value:
            return value
        time.sleep(0.1)
    raise SystemExit("timed out: %s" % desc)


def main():
    if "IMAGE_ID=aspartame" not in Path("/etc/os-release").read_text():
        raise SystemExit("run inside the Aspartame guest")
    if os.getuid() == 0:
        reexec_as_session_user()
    import dbus, gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    bus = dbus.SessionBus()
    journal = dbus.Interface(bus.get_object("org.laptop.Journal", "/org/laptop/Journal"),
                             "org.laptop.Journal")
    shell = dbus.Interface(bus.get_object("org.laptop.Shell", "/org/laptop/Shell"),
                           "org.laptop.Shell")
    store = dbus.Interface(bus.get_object("org.laptop.sugar.DataStore",
                                          "/org/laptop/sugar/DataStore"),
                           "org.laptop.sugar.DataStore")

    def processes(marker):
        found = []
        for cmdline in Path("/proc").glob("[0-9]*/cmdline"):
            try:
                args = cmdline.read_bytes().decode().split("\0")
            except OSError:
                continue
            if marker in args and "--activity-id" in args:
                found.append((int(cmdline.parent.name), args[args.index("--activity-id") + 1]))
        return found

    def nodes(pid):
        stack = [Atspi.get_desktop(0)]
        while stack:
            node = stack.pop()
            try:
                if node.get_process_id() == pid:
                    yield node
                count = node.get_child_count()
            except Exception:
                continue
            if node.get_role_name() == "desktop frame" or node.get_process_id() == pid:
                stack.extend(c for c in (node.get_child_at_index(i) for i in range(count)) if c)

    def text_of(node):
        try:
            return Atspi.Text.get_text(node, 0, -1)
        except Exception:
            return ""

    command, args = sys.argv[1], sys.argv[2:]
    if command == "launch":
        bundle, marker = args[0], args[1]
        uid = args[2] if len(args) > 2 else ""
        if processes(marker):
            raise SystemExit("%s is already running" % marker)
        assert journal.LaunchBundle(bundle, uid)
        pid, aid = wait_for("process", lambda: next(iter(processes(marker)), None))
        wait_for("service", lambda: bus.name_has_owner("org.laptop.Activity" + aid))
        wait_for("activation", lambda: shell.ActivateActivity(aid))
        wait_for("accessible tree", lambda: any(True for _ in nodes(pid)))
        time.sleep(1.5)
        print(json.dumps({"pid": pid, "aid": str(aid)}))
    elif command == "focused":
        pid = int(args[0])
        for node in nodes(pid):
            if node.get_state_set().contains(Atspi.StateType.FOCUSED):
                print(json.dumps({"name": node.get_name(), "role": node.get_role_name()}))
                return
        print(json.dumps({"name": None, "role": None}))
    elif command == "text":
        pid, name = int(args[0]), args[1]
        node = next((n for n in nodes(pid) if n.get_name() == name), None)
        if node is None:
            raise SystemExit("no node named %r" % name)
        print(json.dumps({"text": text_of(node)}))
    elif command == "stop":
        pid, aid = int(args[0]), args[1]
        assert shell.StopActivity(aid)
        wait_for("exit", lambda: not Path("/proc/%d" % pid).exists())
        assert not bus.name_has_owner("org.laptop.Activity" + aid)
        if len(args) > 2:
            uid = args[2]
        else:
            rows = wait_for("Journal entry", lambda: store.find(
                dbus.Dictionary({"activity_id": aid}, signature="sv"),
                dbus.Array(["uid"], signature="s"))[0])
            assert len(rows) == 1, rows
            uid = str(rows[0]["uid"])
        print(json.dumps({"uid": uid, "path": str(store.get_filename(uid))}))
    elif command == "names":
        print(json.dumps([[n.get_role_name(), n.get_name(), text_of(n)[:40]]
                          for n in nodes(int(args[0]))]))
    elif command == "payload":
        print(json.dumps({"path": str(store.get_filename(args[0]))}))
    elif command == "a11y":
        pid = int(args[0])
        unnamed, checked = [], 0
        for node in nodes(pid):
            role = node.get_role_name()
            if role not in INTERACTIVE:
                continue
            states = node.get_state_set()
            if not states.contains(Atspi.StateType.SHOWING):
                continue
            checked += 1
            if not (node.get_name() or "").strip():
                children = [node.get_child_at_index(i) for i in range(node.get_child_count())]
                unnamed.append({"role": role, "description": node.get_description(),
                                "children": [[ch.get_role_name(), ch.get_name()]
                                             for ch in children if ch]})
        print(json.dumps({"checked": checked, "unnamed": unnamed}))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
