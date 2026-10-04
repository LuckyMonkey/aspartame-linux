"""Native GTK4 Abacus place-value Activity."""

import json
from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class AbacusActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("Abacus"); self.values = [0] * 5; self._build()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12); root.set_margin_top(28); root.set_margin_bottom(28); root.set_margin_start(32); root.set_margin_end(32); root.set_hexpand(True); root.set_vexpand(True); root.update_property([Gtk.AccessibleProperty.LABEL], ["Abacus place value"])
        title = Gtk.Label(label="Abacus", xalign=0); title.add_css_class("title-1"); root.append(title)
        subtitle = Gtk.Label(label="Set each place from 0 to 9, then read the number below.", xalign=0); subtitle.add_css_class("dim-label"); root.append(subtitle)
        self.value_label = Gtk.Label(label="Value: 0", xalign=0); self.value_label.set_halign(Gtk.Align.CENTER); self.value_label.add_css_class("abacus-value"); root.append(self.value_label)
        self.rods = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4); self.rods.set_halign(Gtk.Align.CENTER)
        rods_frame = Gtk.Frame(label="Place-value rods"); rods_frame.add_css_class("abacus-card"); rods_frame.set_halign(Gtk.Align.CENTER); rods_frame.set_hexpand(False); rods_frame.set_vexpand(False); rods_frame.set_child(self.rods); root.append(rods_frame)
        self._beads = []
        place_names = ("Ten-thousands", "Thousands", "Hundreds", "Tens", "Ones")
        for index in range(5):
            row = Gtk.Grid(column_spacing=12); row.set_halign(Gtk.Align.CENTER); row.add_css_class("abacus-row")
            label = Gtk.Label(label=f"{place_names[index]}  (10^{4-index})", xalign=1); label.set_width_chars(19); row.attach(label, 0, 0, 1, 1)
            minus = Gtk.Button(label="−"); minus.set_size_request(48, 44); minus.set_tooltip_text(f"Decrease {place_names[index]}"); minus.update_property([Gtk.AccessibleProperty.LABEL], [f"Decrease {place_names[index]}"]); minus.connect("clicked", self._change, index, -1); row.attach(minus, 1, 0, 1, 1)
            bead = Gtk.Label(); bead.set_width_chars(23); bead.set_xalign(0.5); bead.add_css_class("abacus-beads"); bead.update_property([Gtk.AccessibleProperty.LABEL], [f"Rod {index + 1} beads"]); row.attach(bead, 2, 0, 1, 1); self._beads.append(bead)
            plus = Gtk.Button(label="+"); plus.set_size_request(48, 44); plus.set_tooltip_text(f"Increase {place_names[index]}"); plus.update_property([Gtk.AccessibleProperty.LABEL], [f"Increase {place_names[index]}"]); plus.connect("clicked", self._change, index, 1); row.attach(plus, 3, 0, 1, 1); self.rods.append(row)
        clear = Gtk.Button(label="Clear"); clear.set_halign(Gtk.Align.CENTER); clear.set_tooltip_text("Reset all rods to zero"); clear.update_property([Gtk.AccessibleProperty.LABEL], ["Clear all rods"]); clear.connect("clicked", self._clear); root.append(clear); self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"frame.abacus-card { border: 2px solid #8aa8b8; border-radius: 10px; padding: 14px 18px; } .abacus-row { padding: 7px 4px; } .abacus-value { font-size: 22px; font-weight: bold; color: #2f88bd; } .abacus-beads { font-size: 28px; letter-spacing: 2px; } button { min-height: 42px; min-width: 42px; border-radius: 19px; }"); display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self._render_beads()

    def _render_beads(self):
        for index, bead in enumerate(self._beads):
            value = self.values[index]
            bead.set_text("● " * value + "○ " * (10 - value))
            bead.update_property([Gtk.AccessibleProperty.LABEL], [
                f"Rod {index + 1}, value {value} of 9"])

    def _change(self, _button, index, delta):
        self.values[index] = max(0, min(9, self.values[index] + delta)); self._update_value(); self._render_beads()

    def _update_value(self): self.value_label.set_text(f"Value: {sum(v * 10 ** (4-i) for i, v in enumerate(self.values))}")

    def _clear(self, _button): self.values = [0] * 5; self._update_value(); self._render_beads()

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
        self._update_value(); self._render_beads()

    def write_file(self, file_path):
        """Save rod values as a JSON Journal object."""
        Path(file_path).write_text(json.dumps({"values": self.values}, sort_keys=True) + "\n", encoding="utf-8")
