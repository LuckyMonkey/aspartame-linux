#!/usr/bin/env python3
"""Join a public GTK4 Activity from a second guest through sugar4 presence."""

import os
from pathlib import Path
import subprocess
import sys
import time


def wait_for(description, callback, timeout=20):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = callback()
        if value is not None:
            return value
        time.sleep(0.25)
    raise RuntimeError(f"timed out waiting for {description}")


def reexec_as_desktop_user():
    if "IMAGE_ID=aspartame" not in Path("/etc/os-release").read_text():
        raise SystemExit("guest-only")
    if os.getuid() != 0:
        return
    pids = subprocess.check_output(
        ["pgrep", "-u", "aspartame", "-f", "/sources/sugar/src/jarabe/main.py"],
        text=True,
    ).splitlines()
    if len(pids) != 1:
        raise SystemExit(f"expected one modern shell, found {pids!r}")
    environment = dict(
        item.split("=", 1)
        for item in Path(f"/proc/{pids[0]}/environ").read_bytes()
        .decode()
        .split("\0")
        if "=" in item
    )
    for option in ("ASPARTAME_PEER_TIMEOUT", "ASPARTAME_PEER_DEBUG"):
        if option in os.environ:
            environment[option] = os.environ[option]
    os.setgroups([])
    os.setgid(1000)
    os.setuid(1000)
    os.execve(sys.executable, [sys.executable, __file__], environment)


reexec_as_desktop_user()

import dbus
from dbus import PROPERTIES_IFACE
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
from sugar4.presence import presenceservice


DBusGMainLoop(set_as_default=True)
ACCOUNT_MANAGER = "org.freedesktop.Telepathy.AccountManager"
ACCOUNT_MANAGER_PATH = "/org/freedesktop/Telepathy/AccountManager"
ACCOUNT_IFACE = "org.freedesktop.Telepathy.Account"
CONNECTION_IFACE = "org.freedesktop.Telepathy.Connection"
REQUESTS_IFACE = "org.freedesktop.Telepathy.Connection.Interface.Requests"
GROUP_IFACE = "org.freedesktop.Telepathy.Channel.Interface.Group"
CHANNEL_IFACE = "org.freedesktop.Telepathy.Channel"
CONTACT_LIST = "org.freedesktop.Telepathy.Channel.Type.ContactList"
BUDDY_INFO = "org.laptop.Telepathy.BuddyInfo"
ACTIVITY_PROPERTIES = "org.laptop.Telepathy.ActivityProperties"


def debug_enabled():
    return os.environ.get("ASPARTAME_PEER_DEBUG", "").lower() not in {
        "",
        "0",
        "false",
        "no",
    }


debug = debug_enabled()


bus = dbus.SessionBus()
manager = dbus.Interface(
    bus.get_object(ACCOUNT_MANAGER, ACCOUNT_MANAGER_PATH),
    ACCOUNT_MANAGER,
)
account_paths = manager.Get(
    "org.freedesktop.Telepathy.AccountManager",
    "ValidAccounts",
    dbus_interface=PROPERTIES_IFACE,
)
account_path = next((path for path in account_paths if "salut" in str(path)), None)
if account_path is None:
    raise SystemExit("no Salut account")

account = bus.get_object(ACCOUNT_MANAGER, account_path)
connection_path = account.Get(ACCOUNT_IFACE, "Connection", dbus_interface=PROPERTIES_IFACE)
if str(connection_path) == "/":
    raise SystemExit("Salut account is not connected")
connection_name = str(connection_path).replace("/", ".")[1:]
connection = bus.get_object(connection_name, connection_path)
requests = dbus.Interface(connection, REQUESTS_IFACE)
buddy_info = dbus.Interface(connection, BUDDY_INFO)
activity_properties = dbus.Interface(connection, ACTIVITY_PROPERTIES)
channel_properties = dbus.Dictionary(
    {
        CHANNEL_IFACE + ".ChannelType": CONTACT_LIST,
        CHANNEL_IFACE + ".TargetHandleType": dbus.UInt32(3),
        CHANNEL_IFACE + ".TargetID": "subscribe",
    },
    signature="sv",
)
_, channel_path, _ = requests.EnsureChannel(channel_properties)
group = dbus.Interface(bus.get_object(connection_name, channel_path), GROUP_IFACE)


def find_public_calculate():
    members = list(group.GetMembers())
    if debug:
        print(f"peer-debug members={members!r}", flush=True)
    for contact_handle in members:
        activities = list(buddy_info.GetActivities(contact_handle))
        if debug:
            print(
                f"peer-debug handle={contact_handle!r} "
                f"activities={activities!r}",
                flush=True,
            )
        for activity_id, room_handle in activities:
            properties = activity_properties.GetProperties(room_handle)
            if debug:
                print(
                    f"peer-debug candidate activity_id={activity_id!s} "
                    f"room_handle={int(room_handle)} "
                    f"name={str(properties.get('name', ''))!r} "
                    f"private={bool(properties.get('private', True))!r} "
                    f"type={str(properties.get('type', ''))!r}",
                    flush=True,
                )
            if (
                str(properties.get("name", "")) == "Calculate Activity"
                and not bool(properties.get("private", True))
                and str(properties.get("type", "")) == "org.aspartame.Calculate"
            ):
                return str(activity_id), int(room_handle)
    return None


try:
    activity_id, room_handle = wait_for(
        "public Calculate Activity", find_public_calculate
    )
except RuntimeError as error:
    raise SystemExit(
        "share-join=BLOCKED phase=discovery "
        f"reason={error}"
    ) from error
pservice = presenceservice.get_instance()
try:
    activity = wait_for(
        "presence Activity object",
        lambda: pservice.get_activity(activity_id, warn_if_none=False),
    )
except RuntimeError as error:
    raise SystemExit(
        "share-join=BLOCKED phase=activity-object "
        f"activity_id={activity_id} reason={error}"
    ) from error

joined = {"success": None, "error": None}
loop = GLib.MainLoop()


def joined_cb(_activity, success, error):
    joined["success"] = bool(success)
    joined["error"] = str(error) if error else None
    loop.quit()


activity.connect("joined", joined_cb)
if activity.props.joined:
    joined_cb(activity, True, None)
else:
    activity.join()
GLib.timeout_add_seconds(int(os.environ.get("ASPARTAME_PEER_TIMEOUT", "20")), loop.quit)
loop.run()

if joined["success"] is not True:
    raise SystemExit(
        "share-join=BLOCKED phase=join "
        f"activity_id={activity_id} "
        f"reason={joined['error'] or 'timeout'}"
    )

print(
    "share-join=PASS "
    f"activity_id={activity_id} room_handle={room_handle} "
    "joined=True contract=sugar4.presence.Activity",
    flush=True,
)
activity.leave()
