"""Native GTK4 four-colour Appel-Haken puzzle Activity."""

import json
from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class AppelHakenActivity(SimpleActivity):
    COLORS = (("Red", "#e45756"), ("Blue", "#57b8ff"), ("Gold", "#f5c542"), ("Green", "#65c18c"))

    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("Appel Haken"); self.values = [0, 1, 2, 3]; self._build(); self._render()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        root.set_margin_top(30); root.set_margin_bottom(30); root.set_margin_start(34); root.set_margin_end(34)
        root.set_hexpand(True); root.set_vexpand(True)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Appel Haken puzzle"])
        title = Gtk.Label(label="Appel Haken", xalign=0); title.add_css_class("title-1"); root.append(title)
        root.append(Gtk.Label(label="Colour adjacent regions differently. Click a region to cycle its colour.", xalign=0))
        panel = Gtk.Frame(label="Colour regions"); panel.set_hexpand(True); panel.set_vexpand(True)
        content = Gtk.Box(); content.set_hexpand(True); content.set_vexpand(True); content.set_halign(Gtk.Align.CENTER); content.set_valign(Gtk.Align.CENTER)
        self.grid = Gtk.Grid(row_spacing=10, column_spacing=10); self.grid.set_halign(Gtk.Align.CENTER); content.append(self.grid); panel.set_child(content); root.append(panel)
        self.status = Gtk.Label(xalign=0); self.status.add_css_class("dim-label"); root.append(self.status)
        reset = Gtk.Button(label="Reset puzzle"); reset.set_halign(Gtk.Align.CENTER); reset.connect("clicked", self._reset); root.append(reset)
        self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"frame { border: 2px solid #8aa8b8; border-radius: 8px; padding: 8px; } button { min-width: 110px; min-height: 48px; border-radius: 18px; font-size: 17px; } button.red { background: #e45756; color: #ffffff; } button.blue { background: #57b8ff; color: #102030; } button.gold { background: #f5c542; color: #302000; } button.green { background: #65c18c; color: #102818; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _render(self):
        child = self.grid.get_first_child()
        while child is not None:
            nxt = child.get_next_sibling(); self.grid.remove(child); child = nxt
        for index, value in enumerate(self.values):
            name, colour = self.COLORS[value]
            button = Gtk.Button(label=name); button.add_css_class(name.lower()); button.update_property([Gtk.AccessibleProperty.LABEL], ["Region %d, %s" % (index + 1, name)]); button.connect("clicked", self._cycle, index); self.grid.attach(button, index % 2, index // 2, 1, 1)
        self.status.set_text("Solved! Four regions use distinct colours." if len(set(self.values)) == 4 else "Choose a colour for each region.")

    def _cycle(self, _button, index):
        self.values[index] = (self.values[index] + 1) % len(self.COLORS); self._render()

    def _reset(self, _button):
        self.values = [0, 1, 2, 3]; self._render()

    def read_file(self, file_path):
        try:
            payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
            values = payload.get("values") if isinstance(payload, dict) else None
            if isinstance(values, list) and len(values) == 4:
                self.values = [int(value) % len(self.COLORS) for value in values]
                self._render()
        except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
            return

    def write_file(self, file_path):
        Path(file_path).write_text(json.dumps({"values": self.values}, sort_keys=True) + "\n", encoding="utf-8")
