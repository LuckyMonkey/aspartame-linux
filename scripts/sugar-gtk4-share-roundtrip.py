#!/usr/bin/env python3
"""Exercise the GTK4 Activity Share button through the live accessibility tree."""

import os
from pathlib import Path
import subprocess
import time


BUNDLE_ID = "org.aspartame.Calculate"
PROCESS_MARKER = "calculateactivity4.CalculateActivity"


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
        return str(interface(
            bus, reference, "org.freedesktop.DBus.Properties"
        ).Get("org.a11y.atspi.Accessible", "Name"))
    except dbus.DBusException:
        return ""


def role_name(bus, reference):
    try:
        return str(interface(
            bus, reference, "org.a11y.atspi.Accessible").GetRoleName())
    except dbus.DBusException:
        return ""


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


def find_named(bus, root, wanted):
    for reference in walk(bus, root):
        if accessible_name(bus, reference) == wanted:
            return reference
    return None


def find_role(bus, root, role, name=None):
    for reference in walk(bus, root):
        if role_name(bus, reference) != role:
            continue
        if name is None or accessible_name(bus, reference) == name:
            return reference
    return None


def find_last_role(bus, root, role, name=None):
    matches = [reference for reference in walk(bus, root)
               if role_name(bus, reference) == role and
               (name is None or accessible_name(bus, reference) == name)]
    return matches[-1] if matches else None


def find_global_name(bus, wanted):
    for root in children(bus, desktop):
        reference = find_named(bus, root, wanted)
        if reference is not None:
            return reference
    return None


def dump_tree(bus):
    for root in children(bus, desktop):
        for reference in walk(bus, root):
            name = accessible_name(bus, reference)
            role = role_name(bus, reference)
            if name or role in ("button", "menu item", "alert"):
                print(f"share-tree role={role!r} name={name!r}", flush=True)


def activate(bus, reference, label):
    try:
        actions = interface(bus, reference, "org.a11y.atspi.Action")
        available = actions.GetActions()
    except dbus.DBusException as error:
        raise RuntimeError(f"{label} has no AT-SPI action: {error}") from error
    if not available or not bool(actions.DoAction(0)):
        raise RuntimeError(f"AT-SPI activation failed: {label}")


def process():
    for path in Path("/proc").glob("[0-9]*/cmdline"):
        try:
            args = path.read_bytes().decode().split("\0")
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
        if PROCESS_MARKER in args:
            return int(path.parent.name), args[args.index("--activity-id") + 1]
    return None


def activity_log_contains(pid, text):
    """Return whether the live Activity has emitted a matching log line."""
    try:
        environ = dict(
            item.split("=", 1)
            for item in Path(f"/proc/{pid}/environ").read_bytes()
            .decode()
            .split("\0")
            if "=" in item
        )
        log_path = Path(environ["SUGAR_ACTIVITY_ROOT"]) / "logs" / "activity.log"
        return text in log_path.read_text(errors="replace")
    except (FileNotFoundError, KeyError, OSError):
        return False


def current_activity_published(activity_id):
    """Check the live BuddyInfo advertisement for this Activity."""
    try:
        bus = dbus.SessionBus()
        manager = dbus.Interface(
            bus.get_object(
                "org.freedesktop.Telepathy.AccountManager",
                "/org/freedesktop/Telepathy/AccountManager",
            ),
            "org.freedesktop.Telepathy.AccountManager",
        )
        accounts = manager.Get(
            "org.freedesktop.Telepathy.AccountManager",
            "ValidAccounts",
            dbus_interface="org.freedesktop.DBus.Properties",
        )
        for account_path in accounts:
            if "salut" not in str(account_path):
                continue
            account = bus.get_object(
                "org.freedesktop.Telepathy.AccountManager", account_path
            )
            connection_path = account.Get(
                "org.freedesktop.Telepathy.Account",
                "Connection",
                dbus_interface="org.freedesktop.DBus.Properties",
            )
            if str(connection_path) == "/":
                continue
            connection_name = str(connection_path).replace("/", ".")[1:]
            connection = bus.get_object(connection_name, connection_path)
            self_handle = connection.Get(
                "org.freedesktop.Telepathy.Connection",
                "SelfHandle",
                dbus_interface="org.freedesktop.DBus.Properties",
            )
            current_id, room_handle = connection.GetCurrentActivity(
                self_handle,
                dbus_interface="org.laptop.Telepathy.BuddyInfo",
            )
            if str(current_id) == activity_id and int(room_handle) != 0:
                return True
    except dbus.DBusException:
        return False
    return False


if "IMAGE_ID=aspartame" not in Path("/etc/os-release").read_text():
    raise SystemExit("guest-only")

if os.getuid() == 0:
    shells = subprocess.check_output(
        ["pgrep", "-u", "aspartame", "-f", "/sources/sugar/src/jarabe/main.py"],
        text=True,
    ).splitlines()
    if len(shells) != 1:
        raise SystemExit(f"expected one modern shell, found {shells!r}")
    env = dict(
        item.split("=", 1)
        for item in Path(f"/proc/{shells[0]}/environ").read_bytes()
        .decode()
        .split("\0")
        if "=" in item
    )
    runtime = Path(env["XDG_RUNTIME_DIR"])
    # Development sessions use GTK4_ROOT/runtime directly; packaged sessions
    # place the private runtime below XDG_RUNTIME_DIR/aspartame-gtk4.
    if (runtime / "at-spi" / "bus_0").exists():
        atspi_runtime = runtime
    else:
        atspi_runtime = runtime / "aspartame-gtk4"
    env["ASPARTAME_ATSPI_BUS"] = (
        f"unix:path={atspi_runtime / 'at-spi' / 'bus_0'}"
    )
    for option in ("ASPARTAME_SHARE_DUMP", "ASPARTAME_SHARE_MODE"):
        if option in os.environ:
            env[option] = os.environ[option]
    interpreter = os.environ.get(
        "GTK4_PYTHON", "/usr/lib/aspartame/gtk4-preview/venv/bin/python"
    )
    os.setgroups([])
    os.setgid(1000)
    os.setuid(1000)
    os.execve(interpreter, [interpreter, __file__], env)


import dbus


runtime = Path(os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}"))
if not (runtime / "at-spi" / "bus_0").exists():
    runtime = runtime / "aspartame-gtk4"
atsPI_address = os.environ.get(
    "ASPARTAME_ATSPI_BUS",
    f"unix:path={runtime / 'at-spi' / 'bus_0'}",
)
atsPI = dbus.bus.BusConnection(atsPI_address)
desktop = ("org.a11y.atspi.Registry", "/org/a11y/atspi/accessible/root")
session = dbus.SessionBus()
journal = dbus.Interface(
    session.get_object("org.laptop.Journal", "/org/laptop/Journal"),
    "org.laptop.Journal",
)
shell = dbus.Interface(
    session.get_object("org.laptop.Shell", "/org/laptop/Shell"),
    "org.laptop.Shell",
)

if process() is not None:
    raise SystemExit("Calculate already running; probe requires a clean launch")

pid = activity_id = None
try:
    assert journal.LaunchBundle(BUNDLE_ID, "")
    pid, activity_id = wait_for("Calculate process", process)
    wait_for(
        "Calculate Activity service",
        lambda: True if session.name_has_owner(
            "org.laptop.Activity" + activity_id
        ) else None,
    )
    app_root = wait_for(
        "Calculate accessibility application",
        lambda: next((root for root in children(atsPI, desktop)
                      if find_named(atsPI, root, "Calculate")), None),
    )
    toolbar_button = wait_for(
        "Activity toolbar button",
        lambda: find_role(atsPI, app_root, "button", ""),
    )
    activate(atsPI, toolbar_button, "Activity toolbar button")
    if os.environ.get("ASPARTAME_SHARE_DUMP"):
        time.sleep(1)
        dump_tree(atsPI)
    share_button = wait_for(
        "named Share button",
        lambda: find_global_name(atsPI, "Share"),
    )
    activate(atsPI, share_button, "Share button")
    if os.environ.get("ASPARTAME_SHARE_DUMP"):
        time.sleep(0.5)
        dump_tree(atsPI)
    neighborhood = wait_for(
        "My Neighborhood share choice",
        lambda: find_global_name(atsPI, "My Neighborhood"),
    )
    activate(atsPI, neighborhood, "My Neighborhood")
    share_mode = os.environ.get("ASPARTAME_SHARE_MODE", "unavailable")
    if share_mode == "unavailable":
        unavailable = wait_for(
            "sharing-unavailable alert",
            lambda: find_named(atsPI, app_root, "Sharing is unavailable"),
        )
        assert unavailable is not None
        outcome = "fallback=visible-alert"
    elif share_mode == "shared":
        wait_for(
            "successful Telepathy share",
            lambda: True
            if activity_log_contains(
                pid, f"Share of activity {activity_id} successful"
            ) or current_activity_published(activity_id)
            else None,
        )
        outcome = "mode=telepathy-share"
    else:
        raise RuntimeError(f"unknown ASPARTAME_SHARE_MODE: {share_mode}")
    print(
        f"share-roundtrip=PASS pid={pid} activity_id={activity_id} "
        f"{outcome}",
        flush=True,
    )
    hold_seconds = int(os.environ.get("ASPARTAME_SHARE_HOLD_SECONDS", "0"))
    if hold_seconds > 0 and share_mode == "shared":
        time.sleep(hold_seconds)
finally:
    if activity_id is not None:
        shell.StopActivity(activity_id)
        wait_for("Calculate cleanup", lambda: None if process() else True)
