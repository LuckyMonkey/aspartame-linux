#!/usr/bin/env python3
"""Prove Home/Activity/Frame/Home/Activity switching with two GTK4 apps."""

import atexit
import os
from pathlib import Path
import subprocess
import sys
import time


MODERN_ATSPI_BUS = ("unix:path=/home/aspartame/Development/"
                    "gtk4-preview/runtime/at-spi/bus_0")
ACTIVITIES = (
    ("org.aspartame.Count", "countactivity4.CountActivity", "Count"),
    ("org.aspartame.Calculate", "calculateactivity4.CalculateActivity", "Calculate"),
)


def wait_for(label, callback):
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        result = callback()
        if result:
            return result
        time.sleep(.1)
    raise RuntimeError(f"Timed out: {label}")


def pin_modern_atspi_bus():
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

    atexit.register(lambda: subprocess.run(
        ["xprop", "-root", "-f", "AT_SPI_BUS", "8s", "-set",
         "AT_SPI_BUS", original], check=False, stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL))


def main():
    if "IMAGE_ID=aspartame" not in Path("/etc/os-release").read_text():
        raise SystemExit("Run inside Aspartame guest")
    if os.getuid() == 0:
        shells = subprocess.check_output(
            ["pgrep", "-u", "aspartame", "-f", "/sources/sugar/src/jarabe/main.py"],
            text=True).splitlines()
        if len(shells) != 1:
            raise SystemExit("Expected exactly one modern shell")
        env = dict(item.split("=", 1) for item in
                   Path(f"/proc/{shells[0]}/environ").read_bytes().decode().split("\0")
                   if "=" in item)
        interpreter = "/home/aspartame/Development/gtk4-preview/venv/bin/python"
        os.setgroups([]); os.setgid(1000); os.setuid(1000)
        os.execve(interpreter, [interpreter, __file__], env)

    import dbus
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    pin_modern_atspi_bus()
    bus = dbus.SessionBus()
    journal = dbus.Interface(bus.get_object("org.laptop.Journal", "/org/laptop/Journal"),
                             "org.laptop.Journal")
    shell = dbus.Interface(bus.get_object("org.laptop.Shell", "/org/laptop/Shell"),
                           "org.laptop.Shell")

    def processes(marker):
        found = []
        for path in Path("/proc").glob("[0-9]*/cmdline"):
            try:
                args = path.read_bytes().decode().split("\0")
            except OSError:
                continue
            if marker in args and "--activity-id" in args:
                found.append((int(path.parent.name), args[args.index("--activity-id") + 1]))
        return found

    def find_text(node, pid, expected, depth=0):
        if depth > 14:
            return None
        if node.get_process_id() == pid:
            try:
                if expected in Atspi.Text.get_text(node, 0, -1):
                    return node
            except Exception:
                pass
        for index in range(node.get_child_count()):
            child = node.get_child_at_index(index)
            if child is not None:
                found = find_text(child, pid, expected, depth + 1)
                if found is not None:
                    return found
        return None

    launched = []
    try:
        for bundle, marker, expected in ACTIVITIES:
            assert journal.LaunchBundle(bundle, "")
            pid, aid = wait_for(f"{bundle} process", lambda: next(iter(processes(marker)), None))
            wait_for(f"{bundle} service", lambda: bus.name_has_owner("org.laptop.Activity" + aid))
            assert shell.ActivateActivity(aid)
            wait_for(f"{bundle} visible", lambda: find_text(Atspi.get_desktop(0), pid, expected))
            launched.append((pid, aid, expected))

        assert shell.ShowHome()
        assert shell.ShowFrame()
        assert shell.ShowHome()
        for pid, aid, expected in launched:
            assert shell.ActivateActivity(aid)
            wait_for(f"return to {expected}", lambda: find_text(Atspi.get_desktop(0), pid, expected))
        print("switching-probe=PASS activities=2 home-frame-home=PASS", flush=True)
    finally:
        for pid, aid, _ in reversed(launched):
            if Path(f"/proc/{pid}").exists():
                shell.StopActivity(aid)
                wait_for("activity cleanup", lambda: not Path(f"/proc/{pid}").exists())


if __name__ == "__main__":
    main()
