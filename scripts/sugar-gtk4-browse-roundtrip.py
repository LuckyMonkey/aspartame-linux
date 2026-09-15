#!/usr/bin/env python3
"""Guest proof of the native GTK4 Browse surface and URL status path."""
import os, subprocess, time
from pathlib import Path

BUNDLE = "org.laptop.WebActivity"
MARKER = "browseactivity4.BrowseActivity"

def wait_for(fn, label):
    for _ in range(150):
        value = fn()
        if value:
            return value
        time.sleep(.1)
    raise RuntimeError(label)

if "IMAGE_ID=aspartame" not in Path("/etc/os-release").read_text():
    raise SystemExit("guest-only")
if os.getuid() == 0:
    shell_pid = subprocess.check_output(["pgrep", "-u", "aspartame", "-f", "/sources/sugar/src/jarabe/main.py"], text=True).splitlines()[0]
    env = dict(x.split("=", 1) for x in Path(f"/proc/{shell_pid}/environ").read_bytes().decode().split("\0") if "=" in x)
    py = "/home/aspartame/Development/gtk4-preview/venv/bin/python"
    os.setgroups([]); os.setgid(1000); os.setuid(1000); os.execve(py, [py, __file__], env)

import dbus, gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

bus = dbus.SessionBus()
journal = dbus.Interface(bus.get_object("org.laptop.Journal", "/org/laptop/Journal"), "org.laptop.Journal")
shell = dbus.Interface(bus.get_object("org.laptop.Shell", "/org/laptop/Shell"), "org.laptop.Shell")

def processes():
    found = []
    for p in Path("/proc").glob("[0-9]*/cmdline"):
        try: args = p.read_bytes().decode().split("\0")
        except OSError: continue
        if MARKER in args and "--activity-id" in args:
            found.append((int(p.parent.name), args[args.index("--activity-id") + 1]))
    return found

def walk(node, pid, depth=0):
    if depth > 14: return []
    out = []
    if node.get_process_id() == pid:
        try: text = Atspi.Text.get_text(node, 0, -1)
        except Exception: text = ""
        out.append((node, text))
    for i in range(node.get_child_count()):
        child = node.get_child_at_index(i)
        if child: out.extend(walk(child, pid, depth + 1))
    return out

assert journal.LaunchBundle(BUNDLE, "")
pid, activity_id = wait_for(lambda: next(iter(processes()), None), "process")
shell.ActivateActivity(activity_id)
rows = lambda: walk(Atspi.get_desktop(0), pid)
wait_for(lambda: next((n for n, t in rows() if "Welcome to Browse" in t), None), "visible Browse")
entry = wait_for(lambda: next((n for n, t in rows() if n.get_role() in (Atspi.Role.ENTRY, Atspi.Role.TEXT) and n.get_name() == "Web address"), None), "URL entry")
Atspi.EditableText.set_text_contents(entry, "https://example.org")
go = wait_for(lambda: next((n for n, t in rows() if n.get_role() == Atspi.Role.PUSH_BUTTON and n.get_name() in ("Load web address", "Go")), None), "Go button")
if go.get_n_actions(): go.get_action().do_action(0)
wait_for(lambda: next((1 for n, t in rows() if "Loaded" in t or "Load failed" in t), None), "load status")
assert shell.StopActivity(activity_id)
wait_for(lambda: not processes(), "cleanup")
print("browse-visible=PASS url-input=PASS load-status=PASS cleanup=PASS", flush=True)
