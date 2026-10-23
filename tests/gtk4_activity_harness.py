"""Build a GTK4 Activity on the host without Sugar.

A stand-in ``sugar4.activity.SimpleActivity`` (a plain Gtk.Window) lets a
test construct the real Activity class, drive its widgets and call
read_file/write_file. Windows are never presented. Tests that use this are
skipped when GTK4 cannot open a display.
"""
import importlib, sys, types
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]


def gtk():
    gi = pytest.importorskip("gi")
    gi.require_version("Gtk", "4.0")
    from gi.repository import Gtk
    if not Gtk.init_check():
        pytest.skip("GTK4 cannot open a display")
    return Gtk


def _install_stub(Gtk):
    if "sugar4.activity" in sys.modules and getattr(sys.modules["sugar4.activity"], "STUB", False):
        return

    class SimpleActivity(Gtk.Window):
        def __init__(self, handle=None):
            super().__init__()
            self.metadata = {}
            self.saved = 0

        def set_canvas(self, widget):
            self.canvas = widget
            self.set_child(widget)

        def save(self):
            self.saved += 1

        def can_close(self):
            return True

    package = types.ModuleType("sugar4")
    package.__path__ = []
    activity = types.ModuleType("sugar4.activity")
    activity.SimpleActivity = SimpleActivity
    activity.STUB = True
    package.activity = activity
    sys.modules["sugar4"] = package
    sys.modules["sugar4.activity"] = activity


def load(package, module, cls):
    Gtk = gtk()
    _install_stub(Gtk)
    path = str(ROOT / "packages" / package)
    if path not in sys.path:
        sys.path.insert(0, path)
    return getattr(importlib.import_module(module), cls)()


def widgets(root, kind=None):
    """Every descendant widget, optionally of one type."""
    stack, found = [root], []
    while stack:
        widget = stack.pop()
        if kind is None or isinstance(widget, kind):
            found.append(widget)
        child = widget.get_first_child()
        while child is not None:
            stack.append(child)
            child = child.get_next_sibling()
    return found


def button(root, label):
    Gtk = gtk()
    return next(b for b in widgets(root, Gtk.Button) if b.get_label() == label)
