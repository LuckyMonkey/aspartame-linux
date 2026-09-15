"""Native GTK4 BlockParty grid-arrangement Activity."""

import json
from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class BlockPartyActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("BlockParty"); self.blocks = [0, 1, 2, 3]; self._build(); self._render()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        root.set_margin_top(30); root.set_margin_bottom(30); root.set_margin_start(34); root.set_margin_end(34)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["BlockParty puzzle"])
        title = Gtk.Label(label="BlockParty", xalign=0); title.add_css_class("title-1"); root.append(title)
        root.append(Gtk.Label(label="Click blocks to rotate the arrangement into order.", xalign=0))
        self.grid = Gtk.Grid(row_spacing=4, column_spacing=4); self.grid.set_halign(Gtk.Align.CENTER); root.append(self.grid)
        self.status = Gtk.Label(xalign=0); self.status.add_css_class("dim-label"); root.append(self.status)
        reset = Gtk.Button(label="Reset puzzle"); reset.connect("clicked", self._reset); root.append(reset)
        self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"button { min-width: 72px; min-height: 60px; border-radius: 12px; font-size: 20px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _render(self):
        child = self.grid.get_first_child()
        while child is not None:
            nxt = child.get_next_sibling(); self.grid.remove(child); child = nxt
        for index, value in enumerate(self.blocks):
            button = Gtk.Button(label=str(value + 1)); button.update_property([Gtk.AccessibleProperty.LABEL], ["Block %d" % (value + 1)]); button.connect("clicked", self._rotate, index); self.grid.attach(button, index % 2, index // 2, 1, 1)
        self.status.set_text("Solved!" if self.blocks == [0, 1, 2, 3] else "Arrange blocks: %s" % " ".join(str(v + 1) for v in self.blocks))

    def _rotate(self, _button, index):
        self.blocks[index], self.blocks[(index + 1) % len(self.blocks)] = self.blocks[(index + 1) % len(self.blocks)], self.blocks[index]; self._render()

    def _reset(self, _button):
        self.blocks = [0, 1, 2, 3]; self._render()

    def read_file(self, file_path):
        try:
            payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
            blocks = payload.get("blocks") if isinstance(payload, dict) else None
            if isinstance(blocks, list) and sorted(blocks) == [0, 1, 2, 3]:
                self.blocks = [int(value) for value in blocks]
                self._render()
        except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
            return

    def write_file(self, file_path):
        Path(file_path).write_text(json.dumps({"blocks": self.blocks}, sort_keys=True) + "\n", encoding="utf-8")
