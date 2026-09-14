"""Native GTK4 Planets orbit Activity."""

import math

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class PlanetsActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("Planets"); self.selected = "Earth"; self._build()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10); root.set_margin_top(24); root.set_margin_bottom(24); root.set_margin_start(30); root.set_margin_end(30); root.update_property([Gtk.AccessibleProperty.LABEL], ["Planets orbit canvas"])
        title = Gtk.Label(label="Planets", xalign=0); title.add_css_class("title-1"); root.append(title)
        self.canvas = Gtk.DrawingArea(); self.canvas.set_content_width(640); self.canvas.set_content_height(380); self.canvas.set_vexpand(True); self.canvas.set_draw_func(self._draw); self.canvas.update_property([Gtk.AccessibleProperty.LABEL], ["Solar system illustration"]); root.append(self.canvas)
        self.info = Gtk.Label(label="Earth — our home planet", xalign=0); root.append(self.info)
        buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        for name in ("Mercury", "Venus", "Earth", "Mars", "Jupiter"):
            button = Gtk.Button(label=name); button.connect("clicked", self._select, name); buttons.append(button)
        root.append(buttons); self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"button { min-height: 42px; border-radius: 19px; }"); display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _select(self, _button, name): self.selected = name; self.info.set_text(f"{name} — selected planet"); self.canvas.queue_draw()

    def _draw(self, _area, cr, width, height):
        cr.set_source_rgb(0.02, 0.04, 0.12); cr.paint(); cx, cy = width / 2, height / 2; cr.set_source_rgb(1, 0.75, 0.1); cr.arc(cx, cy, 18, 0, 2 * math.pi); cr.fill()
        colors = {"Mercury": (0.55, 0.55, 0.55), "Venus": (0.85, 0.55, 0.2), "Earth": (0.2, 0.5, 0.9), "Mars": (0.8, 0.25, 0.15), "Jupiter": (0.75, 0.55, 0.35)}
        for index, name in enumerate(colors):
            radius = 48 + index * 36; cr.set_source_rgb(0.25, 0.3, 0.5); cr.set_line_width(1); cr.arc(cx, cy, radius, 0, 2 * math.pi); cr.stroke(); angle = index * 1.1; px, py = cx + radius * math.cos(angle), cy + radius * math.sin(angle); cr.set_source_rgb(*colors[name]); cr.arc(px, py, 7 if name != "Jupiter" else 12, 0, 2 * math.pi); cr.fill()
