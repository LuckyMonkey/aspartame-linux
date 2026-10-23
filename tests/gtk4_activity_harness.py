"""Run a snippet against a real GTK4 Activity in its own process.

GTK3 and GTK4 cannot share a GI namespace, so each snippet runs in a fresh
interpreter with the ``sugar4`` stub from ``gtk4_harness`` on ``sys.path``
(as test_gtk4_activity_harness.py does). Windows are never presented.
"""
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
STUB = ROOT / "tests/gtk4_harness"


def _usable():
    if not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        return False
    probe = ("import gi; gi.require_version('Gtk', '4.0'); "
             "from gi.repository import Gtk; Gtk.Window()")
    return subprocess.run([sys.executable, "-c", probe], capture_output=True).returncode == 0


GTK4 = _usable()
needs_gtk4 = pytest.mark.skipif(not GTK4, reason="GTK4 or a display is unavailable")

PRELUDE = """
import sys
sys.path[:0] = [{stub!r}, {package!r}, {tests!r}]
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


def button(root, label):
    stack = [root]
    while stack:
        widget = stack.pop()
        if isinstance(widget, Gtk.Button) and widget.get_label() == label:
            return widget
        child = widget.get_first_child()
        while child is not None:
            stack.append(child)
            child = child.get_next_sibling()
    raise LookupError(label)
"""


def run(package, body):
    """Run ``body`` with the package importable; returns its stdout."""
    script = PRELUDE.format(stub=str(STUB), package=str(ROOT / "packages" / package),
                            tests=str(ROOT / "tests")) + textwrap.dedent(body)
    result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True,
                            timeout=90)
    assert result.returncode == 0, result.stderr[-4000:]
    return result.stdout
