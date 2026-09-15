#!/usr/bin/env python3
"""Report which keys another X11 client already holds a passive grab on.

X11 allows only one client to hold a passive grab on a given key/modifier
combination. Asking for one that is already taken fails with BadAccess, so
attempting the grab is a direct, non-destructive test of whether some other
client - here, the classic GTK3 shell's SugarExt.KeyGrabber - still owns a
key after it claims to have released it.

Guest-only. Grabs taken during the probe are released immediately.
"""
import ctypes
import ctypes.util
import sys

BAD_ACCESS = 10
GRAB_MODE_ASYNC = 1
DEFAULT_KEYS = ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "Tab", "a"]

_errors = []


def main():
    path = ctypes.util.find_library("X11")
    if not path:
        raise SystemExit("libX11 not found")
    xlib = ctypes.cdll.LoadLibrary(path)

    class XErrorEvent(ctypes.Structure):
        _fields_ = [
            ("type", ctypes.c_int),
            ("display", ctypes.c_void_p),
            ("resourceid", ctypes.c_ulong),
            ("serial", ctypes.c_ulong),
            ("error_code", ctypes.c_ubyte),
            ("request_code", ctypes.c_ubyte),
            ("minor_code", ctypes.c_ubyte),
        ]

    handler_type = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p,
                                    ctypes.POINTER(XErrorEvent))

    def on_error(_display, event):
        _errors.append(event.contents.error_code)
        return 0

    handler = handler_type(on_error)
    xlib.XSetErrorHandler(handler)

    xlib.XOpenDisplay.restype = ctypes.c_void_p
    display = xlib.XOpenDisplay(None)
    if not display:
        raise SystemExit("cannot open display")
    display = ctypes.c_void_p(display)

    xlib.XDefaultRootWindow.restype = ctypes.c_ulong
    xlib.XDefaultRootWindow.argtypes = [ctypes.c_void_p]
    root = xlib.XDefaultRootWindow(display)

    xlib.XStringToKeysym.restype = ctypes.c_ulong
    xlib.XStringToKeysym.argtypes = [ctypes.c_char_p]
    xlib.XKeysymToKeycode.restype = ctypes.c_ubyte
    xlib.XKeysymToKeycode.argtypes = [ctypes.c_void_p, ctypes.c_ulong]

    keys = sys.argv[1:] or DEFAULT_KEYS
    held = []
    for name in keys:
        keysym = xlib.XStringToKeysym(name.encode())
        if keysym == 0:
            print("%-6s unknown keysym" % name)
            continue
        keycode = xlib.XKeysymToKeycode(display, keysym)
        if keycode == 0:
            print("%-6s no keycode" % name)
            continue

        del _errors[:]
        xlib.XGrabKey(display, ctypes.c_int(keycode), ctypes.c_uint(0),
                      ctypes.c_ulong(root), ctypes.c_int(1),
                      ctypes.c_int(GRAB_MODE_ASYNC),
                      ctypes.c_int(GRAB_MODE_ASYNC))
        xlib.XSync(display, ctypes.c_int(0))
        taken = BAD_ACCESS in _errors

        if not taken:
            xlib.XUngrabKey(display, ctypes.c_int(keycode),
                            ctypes.c_uint(0), ctypes.c_ulong(root))
            xlib.XSync(display, ctypes.c_int(0))
        else:
            held.append(name)
        print("%-6s keycode=%-3d %s" % (
            name, keycode,
            "HELD by another client" if taken else "free"))

    xlib.XCloseDisplay(display)
    print("grabbed-elsewhere=%s" % (",".join(held) if held else "none"))
    return 1 if held else 0


if __name__ == "__main__":
    raise SystemExit(main())
