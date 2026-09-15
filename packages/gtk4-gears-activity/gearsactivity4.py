"""Native GTK4 Gears drawing Activity."""

import math
import json
from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class GearsActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("Gears"); self._phase = 0.0; self._build(); self.status.set_text("Rotation: 0.00 radians")

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        root.set_margin_top(24); root.set_margin_bottom(24); root.set_margin_start(30); root.set_margin_end(30)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Gears canvas"])
        title = Gtk.Label(label="Gears", xalign=0); title.add_css_class("title-1"); root.append(title)
        self.status = Gtk.Label(xalign=0); self.status.add_css_class("dim-label"); root.append(self.status)
        self.canvas = Gtk.DrawingArea(); self.canvas.set_content_width(640); self.canvas.set_content_height(400); self.canvas.set_vexpand(True); self.canvas.set_draw_func(self._draw); self.canvas.update_property([Gtk.AccessibleProperty.LABEL], ["Meshing gears drawing"]); root.append(self.canvas)
        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        turn = Gtk.Button(label="Turn gears"); turn.connect("clicked", self._turn); controls.append(turn)
        reset = Gtk.Button(label="Reset"); reset.connect("clicked", self._reset); controls.append(reset); root.append(controls)
        self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"button { min-height: 42px; border-radius: 19px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _draw(self, _area, cr, width, height):
        cr.set_source_rgb(0.96, 0.96, 0.96); cr.paint()
        self._gear(cr, width * 0.42, height * 0.52, min(width, height) * 0.22, 12, self._phase)
        self._gear(cr, width * 0.67, height * 0.52, min(width, height) * 0.15, 10, -self._phase * 1.2)

    def _gear(self, cr, cx, cy, radius, teeth, phase):
        points = teeth * 2
        cr.new_path()
        for i in range(points):
            angle = phase + 2 * math.pi * i / points; r = radius * (1.0 if i % 2 == 0 else 0.78)
            (cr.move_to if i == 0 else cr.line_to)(cx + r * math.cos(angle), cy + r * math.sin(angle))
        cr.close_path(); cr.set_source_rgb(0.22, 0.45, 0.65); cr.fill_preserve(); cr.set_source_rgb(0.05, 0.12, 0.18); cr.stroke()
        cr.arc(cx, cy, radius * 0.2, 0, 2 * math.pi); cr.set_source_rgb(0.96, 0.96, 0.96); cr.fill()

    def _turn(self, _button):
        self._phase += 0.25; self.status.set_text(f"Rotation: {self._phase:.2f} radians"); self.canvas.queue_draw()

    def _reset(self, _button):
        self._phase = 0.0; self.status.set_text("Rotation: 0.00 radians"); self.canvas.queue_draw()

    def read_file(self, file_path):
        try:
            payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                self._phase = float(payload.get("phase", 0.0))
                self.status.set_text(f"Rotation: {self._phase:.2f} radians")
                self.canvas.queue_draw()
        except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
            return

    def write_file(self, file_path):
        Path(file_path).write_text(json.dumps({"phase": self._phase}, sort_keys=True) + "\n", encoding="utf-8")
