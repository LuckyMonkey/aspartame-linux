"""Native GTK4 Moon phase viewer."""
import math
import json
from pathlib import Path
from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class MoonActivity(SimpleActivity):
    PHASES = ("New moon", "Waxing crescent", "First quarter", "Waxing gibbous",
              "Full moon", "Waning gibbous", "Last quarter", "Waning crescent")

    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Moon")
        self.phase = 0
        self._build()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        root.set_margin_top(24); root.set_margin_bottom(24)
        root.set_margin_start(30); root.set_margin_end(30)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Moon phase viewer"])
        title = Gtk.Label(label="Moon", xalign=0); title.add_css_class("title-1"); root.append(title)
        self.status = Gtk.Label(xalign=0); root.append(self.status)
        self.canvas = Gtk.DrawingArea(); self.canvas.set_content_width(600); self.canvas.set_content_height(420)
        self.canvas.set_hexpand(True); self.canvas.set_vexpand(True)
        self.canvas.update_property([Gtk.AccessibleProperty.LABEL], ["Moon phase illustration"])
        self.canvas.set_draw_func(self._draw); root.append(self.canvas)
        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        for label, delta in (("Previous", -1), ("Next", 1)):
            button = Gtk.Button(label=label); button.update_property([Gtk.AccessibleProperty.LABEL], [f"{label} moon phase"])
            button.connect("clicked", self._step, delta); controls.append(button)
        reset = Gtk.Button(label="Reset"); reset.connect("clicked", self._reset); controls.append(reset)
        root.append(controls); self.set_canvas(root); self._update()
        provider = Gtk.CssProvider(); provider.load_from_data(b"button { min-height: 42px; border-radius: 19px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _update(self):
        self.status.set_text(f"{self.PHASES[self.phase]} · phase {self.phase + 1} of {len(self.PHASES)}")
        self.canvas.queue_draw()

    def _step(self, _button, delta):
        self.phase = (self.phase + delta) % len(self.PHASES); self._update()

    def _reset(self, _button):
        self.phase = 0; self._update()

    def read_file(self, file_path):
        """Restore the selected lunar phase from a JSON Journal object."""
        try:
            payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
            self.phase = int(payload.get("phase", 0)) % len(self.PHASES) if isinstance(payload, dict) else 0
        except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
            self.phase = 0
        self._update()

    def write_file(self, file_path):
        """Save the selected lunar phase as a JSON Journal object."""
        Path(file_path).write_text(json.dumps({"phase": self.phase}, sort_keys=True) + "\n", encoding="utf-8")

    def _draw(self, _area, cr, width, height):
        cr.set_source_rgb(0.04, 0.06, 0.12); cr.paint()
        radius = min(width, height) * 0.28; cx, cy = width / 2, height / 2
        cr.set_source_rgb(0.92, 0.92, 0.78); cr.arc(cx, cy, radius, 0, 2 * math.pi); cr.fill()
        illumination = (1 - math.cos(2 * math.pi * self.phase / len(self.PHASES))) / 2
        if self.phase in (0, 4):
            cr.set_source_rgb(0.04, 0.06, 0.12); cr.arc(cx, cy, radius, 0, 2 * math.pi); cr.fill() if self.phase == 0 else None
        elif self.phase != 4:
            cr.set_source_rgb(0.04, 0.06, 0.12)
            cr.save(); cr.translate(cx, cy); cr.scale(1 - 2 * illumination, 1); cr.arc(0, 0, radius, 0, 2 * math.pi); cr.fill(); cr.restore()
