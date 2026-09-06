#!/usr/bin/env python3
"""Minimal EWMH workspace control for the Aspartame GTK4 preview."""

import argparse
import ctypes
import os
import sys
import time
from ctypes import (
    POINTER,
    Structure,
    Union,
    byref,
    c_char_p,
    c_int,
    c_long,
    c_ubyte,
    c_ulong,
    c_void_p,
)

CLIENT_MESSAGE = 33
SUBSTRUCTURE_NOTIFY_MASK = 1 << 19
SUBSTRUCTURE_REDIRECT_MASK = 1 << 20


class ClientMessageData(Union):
    _fields_ = [
        ("bytes", ctypes.c_char * 20),
        ("shorts", ctypes.c_short * 10),
        ("longs", c_long * 5),
    ]


class ClientMessageEvent(Structure):
    _fields_ = [
        ("type", c_int),
        ("serial", c_ulong),
        ("send_event", c_int),
        ("display", c_void_p),
        ("window", c_ulong),
        ("message_type", c_ulong),
        ("format", c_int),
        ("data", ClientMessageData),
    ]


class XEvent(Union):
    _fields_ = [
        ("type", c_int),
        ("client", ClientMessageEvent),
        ("padding", c_long * 24),
    ]


class Ewmh:
    def __init__(self):
        self.x11 = ctypes.CDLL("libX11.so.6")
        self._declare_functions()
        display_name = os.environ.get("DISPLAY")
        encoded = display_name.encode() if display_name else None
        self.display = self.x11.XOpenDisplay(encoded)
        if not self.display:
            raise RuntimeError("cannot open X display; set DISPLAY")
        self.root = self.x11.XDefaultRootWindow(self.display)

    def _declare_functions(self):
        x11 = self.x11
        x11.XOpenDisplay.argtypes = [c_char_p]
        x11.XOpenDisplay.restype = c_void_p
        x11.XDefaultRootWindow.argtypes = [c_void_p]
        x11.XDefaultRootWindow.restype = c_ulong
        x11.XInternAtom.argtypes = [c_void_p, c_char_p, c_int]
        x11.XInternAtom.restype = c_ulong
        x11.XGetWindowProperty.argtypes = [
            c_void_p, c_ulong, c_ulong, c_long, c_long, c_int, c_ulong,
            POINTER(c_ulong), POINTER(c_int), POINTER(c_ulong),
            POINTER(c_ulong), POINTER(POINTER(c_ubyte)),
        ]
        x11.XGetWindowProperty.restype = c_int
        x11.XSendEvent.argtypes = [
            c_void_p, c_ulong, c_int, c_long, POINTER(XEvent),
        ]
        x11.XSendEvent.restype = c_int
        x11.XSync.argtypes = [c_void_p, c_int]
        x11.XFree.argtypes = [c_void_p]

    def atom(self, name):
        return self.x11.XInternAtom(self.display, name.encode(), False)

    def property_longs(self, window, name):
        actual_type = c_ulong()
        actual_format = c_int()
        count = c_ulong()
        remaining = c_ulong()
        data = POINTER(c_ubyte)()
        status = self.x11.XGetWindowProperty(
            self.display,
            window,
            self.atom(name),
            0,
            4096,
            False,
            0,
            byref(actual_type),
            byref(actual_format),
            byref(count),
            byref(remaining),
            byref(data),
        )
        if status != 0 or not data:
            return []
        try:
            if actual_format.value == 32:
                values = ctypes.cast(data, POINTER(c_ulong))
                return [int(values[index]) for index in range(count.value)]
            return []
        finally:
            self.x11.XFree(data)

    def current_workspace(self):
        values = self.property_longs(self.root, "_NET_CURRENT_DESKTOP")
        if not values:
            raise RuntimeError("window manager does not publish a workspace")
        return values[0]

    def workspace_count(self):
        values = self.property_longs(self.root, "_NET_NUMBER_OF_DESKTOPS")
        return values[0] if values else 0

    def window_for_pid(self, pid, timeout=10.0):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            for window in self.property_longs(self.root, "_NET_CLIENT_LIST"):
                values = self.property_longs(window, "_NET_WM_PID")
                if values and values[0] == pid:
                    return window
            time.sleep(0.1)
        raise RuntimeError(f"no managed X11 window appeared for PID {pid}")

    def _send(self, window, message_name, values):
        event = XEvent()
        event.client.type = CLIENT_MESSAGE
        event.client.serial = 0
        event.client.send_event = True
        event.client.display = self.display
        event.client.window = window
        event.client.message_type = self.atom(message_name)
        event.client.format = 32
        for index, value in enumerate(values[:5]):
            event.client.data.longs[index] = value
        mask = SUBSTRUCTURE_NOTIFY_MASK | SUBSTRUCTURE_REDIRECT_MASK
        if not self.x11.XSendEvent(
                self.display, self.root, False, mask, byref(event)):
            raise RuntimeError(f"window manager rejected {message_name}")
        self.x11.XSync(self.display, False)

    def switch(self, workspace):
        self._send(self.root, "_NET_CURRENT_DESKTOP", [workspace, 0])

    def activate(self, window):
        self._send(window, "_NET_ACTIVE_WINDOW", [2, 0, 0])

    def place(self, window, workspace, fullscreen=False):
        self._send(window, "_NET_WM_DESKTOP", [workspace, 2])
        if fullscreen:
            self._send(
                window,
                "_NET_WM_STATE",
                [1, self.atom("_NET_WM_STATE_FULLSCREEN"), 0, 2],
            )


def parser():
    result = argparse.ArgumentParser(
        description="Control GTK3/GTK4 Sugar test workspaces")
    actions = result.add_subparsers(dest="action", required=True)

    actions.add_parser("status")
    switch = actions.add_parser("switch")
    switch.add_argument("workspace", type=int)

    activate = actions.add_parser("activate")
    activate.add_argument("--pid", type=int, required=True)
    activate.add_argument("--timeout", type=float, default=10.0)

    place = actions.add_parser("place")
    place.add_argument("--pid", type=int, required=True)
    place.add_argument("--workspace", type=int, required=True)
    place.add_argument("--fullscreen", action="store_true")
    place.add_argument("--timeout", type=float, default=10.0)
    return result


def main():
    args = parser().parse_args()
    ewmh = Ewmh()
    if args.action == "status":
        print(f"current={ewmh.current_workspace()}")
        print(f"count={ewmh.workspace_count()}")
        return 0
    if args.action in ("switch", "place"):
        if args.workspace < 0 or args.workspace >= ewmh.workspace_count():
            raise RuntimeError(f"workspace {args.workspace} is unavailable")
    if args.action == "switch":
        ewmh.switch(args.workspace)
        return 0

    window = ewmh.window_for_pid(args.pid, args.timeout)
    if args.action == "activate":
        ewmh.activate(window)
        print(f"active=0x{window:x}")
        return 0

    ewmh.place(window, args.workspace, args.fullscreen)
    print(f"window=0x{window:x}")
    print(f"workspace={args.workspace}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"sugar-x11-workspace: {error}", file=sys.stderr)
        raise SystemExit(2)
