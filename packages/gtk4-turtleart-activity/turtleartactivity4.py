"""Native GTK4 TurtleBlocks drawing Activity."""

import math

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class TurtleArtActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("TurtleBlocks"); self._reset()

    def _reset(self, _button=None):
        self.x = 0.0; self.y = 0.0; self.heading = 0.0; self.lines = []; self._build() if not hasattr(self, "canvas") else self.canvas.queue_draw()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        root.set_margin_top(22); root.set_margin_bottom(22); root.set_margin_start(28); root.set_margin_end(28)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["TurtleBlocks drawing canvas"])
        title = Gtk.Label(label="TurtleBlocks", xalign=0); title.add_css_class("title-1"); root.append(title)
        self.canvas = Gtk.DrawingArea(); self.canvas.set_content_width(640); self.canvas.set_content_height(420); self.canvas.set_vexpand(True); self.canvas.set_draw_func(self._draw); self.canvas.update_property([Gtk.AccessibleProperty.LABEL], ["Turtle drawing"]); root.append(self.canvas)
        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        for label, callback in (("Forward", self._forward), ("Turn right", self._turn), ("Clear", self._reset)):
            button = Gtk.Button(label=label); button.connect("clicked", callback); controls.append(button)
        root.append(controls); self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"button { min-height: 42px; border-radius: 19px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _forward(self, _button):
        old = (self.x, self.y); self.x += math.cos(self.heading) * 35; self.y += math.sin(self.heading) * 35; self.lines.append((old, (self.x, self.y))); self.canvas.queue_draw()

    def _turn(self, _button):
        self.heading += math.pi / 2; self.canvas.queue_draw()

    def _draw(self, _area, cr, width, height):
        cr.set_source_rgb(0.96, 0.96, 0.96); cr.paint(); ox, oy = width / 2, height / 2
        cr.set_source_rgb(0.12, 0.40, 0.65); cr.set_line_width(4)
        for (x1, y1), (x2, y2) in self.lines: cr.move_to(ox + x1, oy + y1); cr.line_to(ox + x2, oy + y2)
        cr.stroke(); tx, ty = ox + self.x, oy + self.y; cr.arc(tx, ty, 10, 0, 2 * math.pi); cr.set_source_rgb(0.85, 0.25, 0.18); cr.fill()
