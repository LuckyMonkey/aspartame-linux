"""Native GTK4 Abacus place-value Activity."""

import json
from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class AbacusActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("Abacus"); self.values = [0] * 5; self._build()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12); root.set_margin_top(28); root.set_margin_bottom(28); root.set_margin_start(32); root.set_margin_end(32); root.update_property([Gtk.AccessibleProperty.LABEL], ["Abacus place value"])
        title = Gtk.Label(label="Abacus", xalign=0); title.add_css_class("title-1"); root.append(title)
        self.value_label = Gtk.Label(label="Value: 0", xalign=0); root.append(self.value_label)
        self.rods = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8); self.rods.set_vexpand(True); root.append(self.rods)
        for index in range(5):
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8); label = Gtk.Label(label=f"10^{4-index}", width_chars=6); row.append(label)
            minus = Gtk.Button(label="−"); minus.connect("clicked", self._change, index, -1); row.append(minus)
            bead = Gtk.Label(label="○ ○ ○ ○ ○ ○ ○ ○ ○ ○", hexpand=True); bead.set_halign(Gtk.Align.CENTER); bead.update_property([Gtk.AccessibleProperty.LABEL], [f"Rod {index + 1} beads"]); row.append(bead)
            plus = Gtk.Button(label="+"); plus.connect("clicked", self._change, index, 1); row.append(plus); self.rods.append(row)
        clear = Gtk.Button(label="Clear"); clear.connect("clicked", self._clear); root.append(clear); self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"button { min-height: 42px; min-width: 42px; border-radius: 19px; }"); display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _change(self, _button, index, delta):
        self.values[index] = max(0, min(9, self.values[index] + delta)); self._update_value()

    def _update_value(self): self.value_label.set_text(f"Value: {sum(v * 10 ** (4-i) for i, v in enumerate(self.values))}")

    def _clear(self, _button): self.values = [0] * 5; self._update_value()

    def read_file(self, file_path):
        """Restore rod values from a JSON Journal object."""
        try:
            payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
            values = payload.get("values", []) if isinstance(payload, dict) else []
            if not isinstance(values, list) or len(values) != 5:
                raise ValueError("values must contain five rods")
            self.values = [max(0, min(9, int(value))) for value in values]
        except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
            self.values = [0] * 5
        self._update_value()

    def write_file(self, file_path):
        """Save rod values as a JSON Journal object."""
        Path(file_path).write_text(json.dumps({"values": self.values}, sort_keys=True) + "\n", encoding="utf-8")
