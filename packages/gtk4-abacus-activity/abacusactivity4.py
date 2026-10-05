"""Native GTK4 Abacus place-value Activity."""

import json
from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class AbacusActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("Abacus"); self.values = [0] * 5; self._build()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        root.set_margin_top(28); root.set_margin_bottom(28)
        root.set_margin_start(32); root.set_margin_end(32)
        root.set_hexpand(True); root.set_vexpand(True)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Abacus place value"])
        title = Gtk.Label(label="Abacus", xalign=0)
        title.add_css_class("abacus-title")
        root.append(title)
        subtitle = Gtk.Label(
            label="Click a bead or use +/− to set each place from 0 to 9, then read the number below.",
            xalign=0, wrap=True)
        subtitle.add_css_class("dim-label")
        root.append(subtitle)

        value_frame = Gtk.Frame(label="Current value")
        value_frame.add_css_class("abacus-card")
        value_frame.set_halign(Gtk.Align.CENTER)
        value_frame.set_size_request(420, -1)
        self.value_label = Gtk.Label(label="Value: 0", xalign=0.5)
        self.value_label.add_css_class("abacus-value")
        self.value_label.set_margin_top(12); self.value_label.set_margin_bottom(12)
        self.value_label.set_margin_start(18); self.value_label.set_margin_end(18)
        self.value_label.update_property([Gtk.AccessibleProperty.LABEL], ["Current abacus value: 0"])
        value_frame.set_child(self.value_label)
        root.append(value_frame)

        self.rods = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        rods_frame = Gtk.Frame(label="Place-value rods")
        rods_frame.add_css_class("abacus-card")
        rods_frame.set_halign(Gtk.Align.CENTER)
        rods_frame.set_hexpand(False); rods_frame.set_vexpand(False)
        rods_frame.set_size_request(760, -1)
        rods_frame.set_child(self.rods)
        root.append(rods_frame)
        self._beads = []
        place_names = ("Ten-thousands", "Thousands", "Hundreds", "Tens", "Ones")
        for index in range(5):
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            row.set_halign(Gtk.Align.CENTER); row.set_hexpand(False)
            row.set_size_request(700, 58); row.add_css_class("abacus-row")
            label = Gtk.Label(label=f"{place_names[index]}\n10^{4-index}", xalign=0)
            label.set_size_request(170, -1)
            label.set_tooltip_text(f"{place_names[index]} place")
            row.append(label)
            minus = Gtk.Button(label="−")
            minus.set_size_request(48, 44)
            minus.set_tooltip_text(f"Decrease {place_names[index]}")
            minus.update_property([Gtk.AccessibleProperty.LABEL], [f"Decrease {place_names[index]}"])
            minus.connect("clicked", self._change, index, -1)
            row.append(minus)
            bead_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
            bead_box.set_size_request(340, 44)
            bead_box.set_halign(Gtk.Align.CENTER)
            bead_buttons = []
            for bead_index in range(10):
                bead = Gtk.Button(label="○")
                bead.set_size_request(30, 42)
                bead.add_css_class("abacus-bead")
                bead.set_tooltip_text(f"Set {place_names[index]} to {bead_index + 1}")
                bead.update_property(
                    [Gtk.AccessibleProperty.LABEL, Gtk.AccessibleProperty.DESCRIPTION],
                    [
                        f"Set {place_names[index]} to {bead_index + 1}",
                        f"Move the {bead_index + 1}th bead on the {place_names[index]} rod",
                    ],
                )
                bead.connect("clicked", self._set_digit, index, bead_index + 1)
                bead_box.append(bead)
                bead_buttons.append(bead)
            row.append(bead_box)
            self._beads.append(bead_buttons)
            plus = Gtk.Button(label="+")
            plus.set_size_request(48, 44)
            plus.set_tooltip_text(f"Increase {place_names[index]}")
            plus.update_property([Gtk.AccessibleProperty.LABEL], [f"Increase {place_names[index]}"])
            plus.connect("clicked", self._change, index, 1)
            row.append(plus)
            self.rods.append(row)
        clear = Gtk.Button(label="Clear")
        clear.set_halign(Gtk.Align.CENTER)
        clear.set_tooltip_text("Reset all rods to zero")
        clear.update_property([Gtk.AccessibleProperty.LABEL], ["Clear all rods"])
        clear.connect("clicked", self._clear)
        root.append(clear)
        self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"frame.abacus-card { border: 2px solid #8aa8b8; border-radius: 10px; padding: 14px 18px; } box.abacus-row { padding: 7px 4px; } label.abacus-title { font-size: 26px; font-weight: bold; } label.abacus-value { font-size: 22px; font-weight: bold; color: #2f88bd; } button { min-height: 42px; min-width: 42px; border-radius: 19px; } button.abacus-bead { min-width: 28px; padding: 0; font-size: 20px; } button.abacus-bead.filled { color: #2f88bd; font-weight: bold; }"); display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self._render_beads()

    def _render_beads(self):
        for index, beads in enumerate(self._beads):
            value = self.values[index]
            for bead_index, bead in enumerate(beads):
                filled = bead_index < value
                bead.set_label("●" if filled else "○")
                bead.remove_css_class("filled")
                if filled:
                    bead.add_css_class("filled")
                bead.update_property([Gtk.AccessibleProperty.LABEL], [
                    f"Set rod {index + 1} to {bead_index + 1}; current value {value}"])

    def _set_digit(self, _button, index, value):
        self.values[index] = value
        self._update_value()
        self._render_beads()

    def _change(self, _button, index, delta):
        self.values[index] = max(0, min(9, self.values[index] + delta)); self._update_value(); self._render_beads()

    def _update_value(self):
        value = sum(v * 10 ** (4-i) for i, v in enumerate(self.values))
        self.value_label.set_text(f"Value: {value:,}")
        self.value_label.update_property([Gtk.AccessibleProperty.LABEL], [f"Current abacus value: {value}"])

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
