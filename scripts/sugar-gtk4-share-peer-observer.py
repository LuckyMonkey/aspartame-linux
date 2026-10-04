#!/usr/bin/env python3
"""Observe a public GTK4 Activity arriving through Telepathy on a peer."""

import os
from pathlib import Path
import subprocess
import sys


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
    env = dict(
        item.split("=", 1)
        for item in Path(f"/proc/{pids[0]}/environ").read_bytes()
        .decode()
        .split("\0")
        if "=" in item
    )
    for option in ("ASPARTAME_PEER_DEBUG", "ASPARTAME_PEER_TIMEOUT"):
        if option in os.environ:
            env[option] = os.environ[option]
    os.setgroups([])
    os.setgid(1000)
    os.setuid(1000)
    os.execve(sys.executable, [sys.executable, __file__], env)


reexec_as_desktop_user()

import dbus
from dbus import PROPERTIES_IFACE
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib


DBusGMainLoop(set_as_default=True)

ACCOUNT_MANAGER_SERVICE = "org.freedesktop.Telepathy.AccountManager"
ACCOUNT_MANAGER_PATH = "/org/freedesktop/Telepathy/AccountManager"
ACCOUNT_MANAGER_IFACE = "org.freedesktop.Telepathy.AccountManager"
ACCOUNT_IFACE = "org.freedesktop.Telepathy.Account"
REQUESTS_IFACE = "org.freedesktop.Telepathy.Connection.Interface.Requests"
GROUP_IFACE = "org.freedesktop.Telepathy.Channel.Interface.Group"
CHANNEL_IFACE = "org.freedesktop.Telepathy.Channel"
CHANNEL_TYPE_CONTACT_LIST = "org.freedesktop.Telepathy.Channel.Type.ContactList"
BUDDY_INFO_IFACE = "org.laptop.Telepathy.BuddyInfo"
ACTIVITY_PROPERTIES_IFACE = "org.laptop.Telepathy.ActivityProperties"

timeout = int(os.environ.get("ASPARTAME_PEER_TIMEOUT", "15"))
debug = bool(os.environ.get("ASPARTAME_PEER_DEBUG"))
bus = dbus.SessionBus()
manager = dbus.Interface(
    bus.get_object(ACCOUNT_MANAGER_SERVICE, ACCOUNT_MANAGER_PATH),
    ACCOUNT_MANAGER_IFACE,
)
account_paths = manager.Get(
    "org.freedesktop.Telepathy.AccountManager",
    "ValidAccounts",
    dbus_interface=PROPERTIES_IFACE,
)
account_path = next((path for path in account_paths if "salut" in str(path)), None)
if account_path is None:
    raise SystemExit("no Salut account")

account = bus.get_object(ACCOUNT_MANAGER_SERVICE, account_path)
connection_path = account.Get(
    ACCOUNT_IFACE, "Connection", dbus_interface=PROPERTIES_IFACE
)
if str(connection_path) == "/":
    raise SystemExit("Salut account is not connected")

connection_name = str(connection_path).replace("/", ".")[1:]
connection = bus.get_object(connection_name, connection_path)
requests = dbus.Interface(connection, REQUESTS_IFACE)
buddy_info = dbus.Interface(connection, BUDDY_INFO_IFACE)
activity_properties = dbus.Interface(connection, ACTIVITY_PROPERTIES_IFACE)
channel_properties = dbus.Dictionary(
    {
        CHANNEL_IFACE + ".ChannelType": CHANNEL_TYPE_CONTACT_LIST,
        CHANNEL_IFACE + ".TargetHandleType": dbus.UInt32(3),
        CHANNEL_IFACE + ".TargetID": "subscribe",
    },
    signature="sv",
)
_, channel_path, _ = requests.EnsureChannel(channel_properties)
group = dbus.Interface(
    bus.get_object(connection_name, channel_path), GROUP_IFACE
)
loop = GLib.MainLoop()
found = []
seen_rooms = set()


def got_properties(activity_id, room_handle, properties):
    name = str(properties.get("name", ""))
    private = bool(properties.get("private", True))
    bundle_type = str(properties.get("type", ""))
    if name != "Calculate Activity" or private:
        return
    found.append(activity_id)
    print(
        "share-peer=PASS "
        f"activity_id={activity_id} room_handle={room_handle} "
        f"name={name!r} private={private} type={bundle_type!r}",
        flush=True,
    )
    loop.quit()


def poll_activities():
    try:
        members = group.GetMembers()
        if debug:
            print(f"peer-debug members={list(members)!r}", flush=True)
        for contact_handle in members:
            activities = buddy_info.GetActivities(contact_handle)
            if debug:
                print(
                    f"peer-debug handle={contact_handle!r} "
                    f"activities={list(activities)!r}",
                    flush=True,
                )
            for activity_id, room_handle in activities:
                room_key = (int(contact_handle), int(room_handle))
                if room_key in seen_rooms:
                    continue
                seen_rooms.add(room_key)
                activity_properties.GetProperties(
                    room_handle,
                    reply_handler=lambda properties,
                    activity_id=activity_id,
                    room_handle=room_handle: got_properties(
                        str(activity_id), room_handle, properties
                    ),
                    error_handler=lambda error: None,
                )
    except dbus.DBusException as error:
        if debug:
            print(f"peer-debug error={error}", flush=True)
    return not found


GLib.timeout_add(500, poll_activities)
GLib.timeout_add_seconds(timeout, loop.quit)
loop.run()

if not found:
    raise SystemExit(f"timed out waiting for public Calculate Activity ({timeout}s)")
