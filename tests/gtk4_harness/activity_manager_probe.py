"""Build the GTK4 Activity Manager headlessly and exercise face ratings.

Runs in its own process with stub ``jarabe`` modules and a scratch HOME.
Prints ``activity-manager-faces=PASS``.
"""

import json
import os
import sys
import tempfile
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HOME = tempfile.mkdtemp(prefix="am-home-")
os.environ["HOME"] = HOME
config = Path(HOME, ".config/aspartame")
config.mkdir(parents=True)
LEGACY = config / "activity-ratings.json"
LEGACY.write_text(json.dumps({"org.sugarlabs.Write": 5, "org.laptop.Terminal": 1}))
LEGACY_BYTES = LEGACY.read_bytes()

import gi  # noqa: E402

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402

for name in ("jarabe", "jarabe.model", "jarabe.controlpanel"):
    sys.modules[name] = types.ModuleType(name)
registry = types.ModuleType("jarabe.model.bundleregistry")
registry.get_registry = lambda: []
sys.modules["jarabe.model.bundleregistry"] = registry
sectionview = types.ModuleType("jarabe.controlpanel.sectionview")
sectionview.SectionView = type("SectionView", (Gtk.Box,), {
    "__init__": lambda self: Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)})
sys.modules["jarabe.controlpanel.sectionview"] = sectionview
sys.path.insert(0, str(ROOT / "gtk4-overlay/src"))

from cpsection.activities import model, view, wongbaker  # noqa: E402

ACTIVITIES = [
    {"id": "org.sugarlabs.Write", "name": "Write", "version": "1", "path": "/x", "managed": True},
    {"id": "org.laptop.Terminal", "name": "Terminal", "version": "1", "path": "/y", "managed": True},
    {"id": "org.example.Unknown", "name": "Unknown", "version": "1", "path": "/z", "managed": False},
]
model.list_activities = lambda: ACTIVITIES


def labels(widget):
    child = widget.get_first_child()
    while child is not None:
        if isinstance(child, Gtk.Label):
            yield child.get_label()
        yield from labels(child)
        child = child.get_next_sibling()


def faces(widget):
    child = widget.get_first_child()
    while child is not None:
        if isinstance(child, view.FaceRating):
            yield child
        else:
            yield from faces(child)
        child = child.get_next_sibling()


def main():
    manager = view.ActivityManager(model, None)
    rows = list(faces(manager))
    assert len(rows) == 3
    write, terminal, unknown = rows
    # Classic answers appear on the new scale: Perfect -> 0, Broken -> 10.
    assert write.get_score() == 0 and terminal.get_score() == 10
    assert unknown.get_score() is None
    text = list(labels(manager))
    assert any(t == "FUNCTIONAL PORT" for t in text), text
    assert "Not yet compared with GTK3" in text

    unknown.get_buttons()[2].set_active(True)  # score 4
    assert wongbaker.load_ratings()["org.example.Unknown"] == 4
    assert "Rated Unknown: Hurts a little more." in text + list(labels(manager))
    unknown.get_buttons()[3].set_active(True)  # move to 6: one-or-none
    assert unknown.get_score() == 6
    assert sum(b.get_active() for b in unknown.get_buttons()) == 1
    write.get_buttons()[0].set_active(False)   # clear a classic answer
    assert wongbaker.load_ratings()["org.sugarlabs.Write"] is None
    assert LEGACY.read_bytes() == LEGACY_BYTES, "classic ratings must never be rewritten"

    for button in write.get_buttons():
        assert button.get_tooltip_text()
    resumed = view.ActivityManager(model, None)
    again = list(faces(resumed))
    assert again[0].get_score() is None and again[2].get_score() == 6
    print("activity-manager-faces=PASS")


if __name__ == "__main__":
    main()
