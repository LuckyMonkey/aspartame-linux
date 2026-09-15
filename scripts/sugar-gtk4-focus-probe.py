#!/usr/bin/env python3
"""Report the AT-SPI-focused accessible in the live modern Space.

Physical Tab/Shift+Tab delivery has been proven at the QEMU/evdev transport
level (see reports/gtk4/qemu-function-keys-20260915.md), but a screenshot
alone cannot tell a transport failure apart from a real focus move that
simply has no visible ring. This probe answers that question directly from
AT-SPI, independent of rendering.

GTK4-023: the shared X display's root-window AT_SPI_BUS property names only
one accessibility bus at a time, owned by whichever Space's private
at-spi-bus-launcher started most recently. libatspi (current at-spi2-core)
does not honor an AT_SPI_BUS environment-variable override, so a probe that
inherits the modern Space's own process environment still silently follows
the shared X property and can land on the classic GTK3 Space's registry
instead - `Atspi.get_desktop()` then enumerates metacity/-m/datastore-service
(GTK3-side) rather than the modern shell, with no error. This probe pins the
property to the modern Space's own deterministic bus socket for the
duration of the query, then restores whatever address was there before, so
neither Space's own already-established AT-SPI connections are disturbed.

Run from the host: it re-execs itself as the aspartame user inside the GTK4
preview's own venv, matching sugar-gtk4-help-visible.py's boundary.
"""
import os
import subprocess
import sys
from pathlib import Path

if "IMAGE_ID=aspartame" not in Path("/etc/os-release").read_text():
    raise SystemExit("guest-only")
if os.getuid() == 0:
    pid = subprocess.check_output(
        ["pgrep", "-u", "aspartame", "-f", "/sources/sugar/src/jarabe/main.py"],
        text=True).splitlines()[0]
    env = dict(x.split("=", 1) for x in
               Path(f"/proc/{pid}/environ").read_bytes().decode().split("\0")
               if "=" in x)
    py = "/home/aspartame/Development/gtk4-preview/venv/bin/python"
    os.setgroups([])
    os.setgid(1000)
    os.setuid(1000)
    os.execve(py, [py, __file__] + sys.argv[1:], env)

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

MODERN_BUS = ("unix:path=/home/aspartame/Development/"
              "gtk4-preview/runtime/at-spi/bus_0")


def _xprop(*args):
    return subprocess.run(["xprop", "-root", *args],
                           capture_output=True, text=True, check=True)


def _read_at_spi_bus():
    result = _xprop("AT_SPI_BUS")
    # 'AT_SPI_BUS(STRING) = "unix:path=...,guid=..."'
    _, _, value = result.stdout.partition("= ")
    return value.strip().strip('"')


def _write_at_spi_bus(address):
    _xprop("-f", "AT_SPI_BUS", "8s", "-set", "AT_SPI_BUS", address)


def describe(node):
    try:
        name = node.get_name() or ""
    except Exception:
        name = ""
    try:
        role = node.get_role_name()
    except Exception:
        role = "?"
    try:
        pid = node.get_process_id()
    except Exception:
        pid = -1
    parents = []
    parent = node
    for _ in range(6):
        try:
            parent = parent.get_parent()
        except Exception:
            break
        if parent is None:
            break
        try:
            parents.append(parent.get_name() or parent.get_role_name())
        except Exception:
            break
    return name, role, pid, " < ".join(parents)


def find_focused(node, depth=0, matches=None):
    if matches is None:
        matches = []
    if depth > 20:
        return matches
    try:
        states = node.get_state_set()
        if states.contains(Atspi.StateType.FOCUSED):
            matches.append(node)
    except Exception:
        pass
    try:
        count = node.get_child_count()
    except Exception:
        count = 0
    for i in range(count):
        try:
            child = node.get_child_at_index(i)
        except Exception:
            continue
        if child is not None:
            find_focused(child, depth + 1, matches)
    return matches


def main():
    original_bus = _read_at_spi_bus()
    _write_at_spi_bus(MODERN_BUS)
    try:
        desktop = Atspi.get_desktop(0)
        matches = find_focused(desktop)
        if not matches:
            apps = []
            for i in range(desktop.get_child_count()):
                app = desktop.get_child_at_index(i)
                if app is None:
                    continue
                try:
                    apps.append("%s(pid=%d,children=%d)" % (
                        app.get_name(), app.get_process_id(),
                        app.get_child_count()))
                except Exception as error:
                    apps.append("<error %s>" % error)
            print("focused=none apps=%d [%s]" % (len(apps), ", ".join(apps)))
            return 1
        for node in matches:
            name, role, pid, breadcrumb = describe(node)
            print("focused=1 pid=%d role=%s name=%r path=%s" %
                  (pid, role, name, breadcrumb))
        return 0
    finally:
        _write_at_spi_bus(original_bus)


if __name__ == "__main__":
    raise SystemExit(main())
