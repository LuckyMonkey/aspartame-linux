"""Keep GTK windows from tests off the desktop.

GTK tests construct real windows (and the click-every-button harness hits
Fullscreen and file-picker buttons), which flash on the user's screen. Every
pytest run therefore gets a private Xvfb display; DISPLAY points at it and
WAYLAND_DISPLAY is dropped, so the test process and all its subprocesses
draw there. Without Xvfb the display variables are cleared and GTK tests
skip rather than use the real desktop.
"""
import os
import shutil
import subprocess

_xvfb = None


def pytest_configure(config):
    global _xvfb
    os.environ.pop("WAYLAND_DISPLAY", None)
    os.environ.pop("DISPLAY", None)
    if shutil.which("Xvfb") is None:
        return
    read, write = os.pipe()
    _xvfb = subprocess.Popen(["Xvfb", "-displayfd", str(write), "-screen", "0", "1280x800x24",
                              "-nolisten", "tcp"], pass_fds=(write,),
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.close(write)
    with os.fdopen(read) as stream:
        number = stream.readline().strip()
    if number:
        os.environ["DISPLAY"] = ":" + number
    # No portal or real session bus: file dialogs must not reach the desktop.
    os.environ["GTK_USE_PORTAL"] = "0"
    os.environ["GDK_BACKEND"] = "x11"
    os.environ["DBUS_SESSION_BUS_ADDRESS"] = "unix:path=/nonexistent/aspartame-test-bus"


def pytest_unconfigure(config):
    if _xvfb is not None:
        _xvfb.terminate()
        _xvfb.wait(timeout=10)
