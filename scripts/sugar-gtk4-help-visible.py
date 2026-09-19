#!/usr/bin/env python3
"""Launch Help in the modern Space, activate it, and report visible text."""
import atexit
import os, subprocess, time
from pathlib import Path

MODERN_ATSPI_BUS = ("unix:path=/home/aspartame/Development/"
                    "gtk4-preview/runtime/at-spi/bus_0")


def pin_modern_atspi_bus():
    """Keep Help accessibility queries on the modern Space's bus."""
    try:
        result = subprocess.run(["xprop", "-root", "AT_SPI_BUS"],
                                capture_output=True, text=True, check=True)
        _, _, value = result.stdout.partition("= ")
        original = value.strip().strip('"')
        subprocess.run(["xprop", "-root", "-f", "AT_SPI_BUS", "8s",
                        "-set", "AT_SPI_BUS", MODERN_ATSPI_BUS], check=True,
                       stdout=subprocess.DEVNULL)
    except (OSError, subprocess.CalledProcessError):
        return

    def restore():
        subprocess.run(["xprop", "-root", "-f", "AT_SPI_BUS", "8s",
                        "-set", "AT_SPI_BUS", original],
                       check=False, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
    atexit.register(restore)

if "IMAGE_ID=aspartame" not in Path("/etc/os-release").read_text():
    raise SystemExit("guest-only")
if os.getuid() == 0:
    pid = subprocess.check_output(["pgrep", "-u", "aspartame", "-f", "/sources/sugar/src/jarabe/main.py"], text=True).splitlines()[0]
    env = dict(x.split("=", 1) for x in Path(f"/proc/{pid}/environ").read_bytes().decode().split("\0") if "=" in x)
    py = "/home/aspartame/Development/gtk4-preview/venv/bin/python"
    os.setgroups([]); os.setgid(1000); os.setuid(1000); os.execve(py, [py, __file__], env)
import dbus
from gi.repository import Atspi
pin_modern_atspi_bus()
bus = dbus.SessionBus()
journal = dbus.Interface(bus.get_object("org.laptop.Journal", "/org/laptop/Journal"), "org.laptop.Journal")
shell = dbus.Interface(bus.get_object("org.laptop.Shell", "/org/laptop/Shell"), "org.laptop.Shell")
def find(node, pid, depth=0):
    if depth > 14: return None
    if node.get_process_id() == pid:
        try: text = Atspi.Text.get_text(node, 0, -1)
        except Exception: text = ""
        try: name = node.get_name() or ""
        except Exception: name = ""
        if "Sugar Help" in text or "Sugar Help" in name or "How Sugar is organized" in text:
            return node, text, name
    for i in range(node.get_child_count()):
        child = node.get_child_at_index(i)
        if child:
            hit = find(child, pid, depth + 1)
            if hit: return hit
    return None
def find_entry(node, pid, depth=0):
    if depth > 14: return None
    if node.get_process_id() == pid and node.get_role() in (Atspi.Role.ENTRY, Atspi.Role.TEXT):
        try:
            if node.get_name() == "Search help" or node.get_role() == Atspi.Role.ENTRY:
                return node
        except Exception:
            pass
    for i in range(node.get_child_count()):
        child = node.get_child_at_index(i)
        if child:
            hit = find_entry(child, pid, depth + 1)
            if hit: return hit
    return None
old_pids = subprocess.run(["pgrep", "-u", "aspartame", "-f", "helpactivity4.HelpActivity"], text=True, capture_output=True).stdout.splitlines()
for old in old_pids:
    try: os.kill(int(old), 15)
    except ProcessLookupError: pass
time.sleep(1)
assert journal.LaunchBundle("org.laptop.HelpActivity", "")
pid = None
for _ in range(150):
    rows = subprocess.check_output(["pgrep", "-u", "aspartame", "-f", "helpactivity4.HelpActivity"], text=True).splitlines()
    if rows: pid = int(rows[0]); break
    time.sleep(.1)
assert pid
aid = None
for _ in range(100):
    args = Path(f"/proc/{pid}/cmdline").read_bytes().decode().split("\0")
    if "--activity-id" in args: aid = args[args.index("--activity-id") + 1]; break
    time.sleep(.1)
assert aid
print("activate", aid, shell.ActivateActivity(aid), flush=True)
hit = None
for _ in range(100):
    hit = find(Atspi.get_desktop(0), pid)
    if hit: break
    time.sleep(.1)
assert hit, "Help surface not visible in AT-SPI"
entry = find_entry(Atspi.get_desktop(0), pid)
assert entry, "Help search entry not visible in AT-SPI"
Atspi.EditableText.set_text_contents(entry, "Journal")
filtered = None
for _ in range(100):
    def has_match(node, depth=0):
        if depth > 14: return False
        if node.get_process_id() == pid:
            try:
                text = Atspi.Text.get_text(node, 0, -1)
                if "topic match" in text or "topics match" in text: return True
            except Exception: pass
        for i in range(node.get_child_count()):
            child = node.get_child_at_index(i)
            if child and has_match(child, depth + 1): return True
        return False
    if has_match(Atspi.get_desktop(0)): break
    time.sleep(.1)
assert has_match(Atspi.get_desktop(0)), "Help search did not filter Journal topic"
print("help-visible=PASS help-search=PASS pid=%d activity=%s" % (pid, aid), flush=True)
