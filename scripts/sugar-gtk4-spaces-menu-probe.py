#!/usr/bin/env python3
"""Exercise the GTK4 Home Spaces menu through its AT-SPI D-Bus surface."""

import dbus
import os
from pathlib import Path
import subprocess
import time


def wait_for(label, callback, timeout=15):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        result = callback()
        if result is not None:
            return result
        time.sleep(0.1)
    raise RuntimeError(f"timed out: {label}")


def interface(bus, reference, name):
    destination, object_path = reference
    return dbus.Interface(bus.get_object(str(destination), str(object_path)), name)


def children(bus, reference):
    return [tuple(item) for item in interface(
        bus, reference, "org.a11y.atspi.Accessible").GetChildren()]


def accessible_name(bus, reference):
    try:
        value = interface(
            bus, reference, "org.freedesktop.DBus.Properties"
        ).Get("org.a11y.atspi.Accessible", "Name")
        return str(value)
    except dbus.DBusException:
        return ""


def role_name(bus, reference):
    try:
        return str(interface(
            bus, reference, "org.a11y.atspi.Accessible"
        ).GetRoleName())
    except dbus.DBusException:
        return ""


def interfaces(bus, reference):
    try:
        return [str(item) for item in interface(
            bus, reference, "org.a11y.atspi.Accessible"
        ).GetInterfaces()]
    except dbus.DBusException:
        return []


def walk(bus, reference, depth=0):
    if depth > 18:
        return
    yield reference
    try:
        descendants = children(bus, reference)
    except dbus.DBusException:
        return
    for child in descendants:
        yield from walk(bus, child, depth + 1)


def find_named(bus, roots, wanted):
    for root in roots:
        for reference in walk(bus, root):
            if accessible_name(bus, reference) == wanted:
                return reference
    return None


def activate(bus, reference, label):
    try:
        actions = interface(bus, reference, "org.a11y.atspi.Action")
        available = actions.GetActions()
    except dbus.DBusException as error:
        raise RuntimeError(f"{label} has no AT-SPI action: {error}") from error
    if not available:
        raise RuntimeError(f"{label} has no AT-SPI action")
    if not bool(actions.DoAction(0)):
        raise RuntimeError(f"AT-SPI activation failed: {label}")


if "IMAGE_ID=aspartame" not in Path("/etc/os-release").read_text():
    raise SystemExit("guest-only")
if os.getuid() == 0:
    raise SystemExit("run as the aspartame desktop user")

runtime = Path(os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}"))
address = os.environ.get(
    "ASPARTAME_ATSPI_BUS",
    f"unix:path={runtime / 'aspartame-gtk4' / 'at-spi' / 'bus_0'}",
)
bus = dbus.bus.BusConnection(address)
desktop_root = (
    "org.a11y.atspi.Registry", "/org/a11y/atspi/accessible/root"
)
roots = children(bus, desktop_root)

if os.environ.get("ASPARTAME_ATSPI_DUMP"):
    print(f"accessible-apps={len(roots)}")
    for root in roots:
        print(f"accessible-app={accessible_name(bus, root)!r} ref={root!r}")
        for reference in walk(bus, root):
            item_name = accessible_name(bus, reference)
            item_role = role_name(bus, reference)
            item_interfaces = interfaces(bus, reference)
            if item_name or "org.a11y.atspi.Action" in item_interfaces:
                action_names = []
                if "org.a11y.atspi.Action" in item_interfaces:
                    try:
                        action_names = [str(item[0]) for item in interface(
                            bus, reference, "org.a11y.atspi.Action"
                        ).GetActions()]
                    except dbus.DBusException:
                        pass
                print(
                    f"accessible-role={item_role!r} name={item_name!r} "
                    f"actions={action_names!r} "
                    f"ref={reference!r}"
                )

spaces = wait_for(
    "Spaces button", lambda: find_named(bus, roots, "Spaces")
)
activate(bus, spaces, "Spaces button")
compare = wait_for(
    "Compare Spaces side by side menu item",
    lambda: find_named(bus, roots, "Compare Spaces side by side"),
)
marker = runtime / "aspartame-side-by-side"
marker.unlink(missing_ok=True)
activate(bus, compare, "Compare Spaces side by side")

wait_for("side-by-side marker", lambda: marker if marker.exists() else None)
checker = Path(__file__).with_name("sugar-gtk4-side-by-side-probe.sh")
last_result = None


def check_side_by_side():
    global last_result
    last_result = subprocess.run(
        [str(checker)], capture_output=True, text=True, check=False,
    )
    if last_result.returncode == 0:
        return last_result.stdout.rstrip()
    return None


geometry = wait_for("side-by-side geometry", check_side_by_side, timeout=30)
if geometry:
    print(geometry, flush=True)
if last_result and last_result.stderr:
    print(last_result.stderr.rstrip(), flush=True)
print(
    "spaces-menu=PASS button=Spaces compare-action=PASS "
    f"marker={marker}",
    flush=True,
)
