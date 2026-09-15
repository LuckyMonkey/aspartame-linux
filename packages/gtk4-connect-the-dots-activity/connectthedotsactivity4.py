"""Native GTK4 Connect the Dots Activity.

The puzzle is deliberately small and deterministic so it works offline: click
the numbered points in order to draw a continuous line through the picture.
"""

import json
import math
from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class ConnectTheDotsActivity(SimpleActivity):
    """Connect numbered points with pointer or keyboard activation."""

    POINTS = ((0.18, 0.72), (0.30, 0.28), (0.46, 0.62), (0.62, 0.22),
              (0.80, 0.42), (0.72, 0.78), (0.48, 0.84), (0.30, 0.55))

    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Connect the Dots")
        self._next = 0
        self._connected = []
        self._build()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        root.set_margin_top(24); root.set_margin_bottom(24)
        root.set_margin_start(30); root.set_margin_end(30)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Connect the Dots puzzle"])
        title = Gtk.Label(label="Connect the Dots", xalign=0)
        title.add_css_class("title-1"); root.append(title)
        self.status = Gtk.Label(label="Connect dot 1 to begin", xalign=0)
        root.append(self.status)
        self.canvas = Gtk.DrawingArea()
        self.canvas.set_content_width(640); self.canvas.set_content_height(440)
        self.canvas.set_hexpand(True); self.canvas.set_vexpand(True)
        self.canvas.set_focusable(True)
        self.canvas.update_property([Gtk.AccessibleProperty.LABEL], ["Numbered dot puzzle canvas"])
        self.canvas.set_draw_func(self._draw)
        click = Gtk.GestureClick(); click.connect("pressed", self._pressed)
        self.canvas.add_controller(click); root.append(self.canvas)
        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        reset = Gtk.Button(label="New puzzle"); reset.connect("clicked", self._reset)
        reset.update_property([Gtk.AccessibleProperty.LABEL], ["Start a new Connect the Dots puzzle"])
        controls.append(reset); root.append(controls)
        self.set_canvas(root)
        provider = Gtk.CssProvider()
        provider.load_from_data(b"button { min-height: 42px; border-radius: 19px; }")
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _point(self, index, width, height):
        return self.POINTS[index][0] * width, self.POINTS[index][1] * height

    def _draw(self, _area, cr, width, height):
        cr.set_source_rgb(0.97, 0.97, 0.97); cr.paint()
        cr.set_line_width(4); cr.set_line_cap(1); cr.set_source_rgb(0.12, 0.47, 0.67)
        for index in range(1, len(self._connected)):
            cr.move_to(*self._point(self._connected[index - 1], width, height))
            cr.line_to(*self._point(self._connected[index], width, height)); cr.stroke()
        for index in range(len(self.POINTS)):
            x, y = self._point(index, width, height)
            cr.set_source_rgb(0.12, 0.47, 0.67) if index < self._next else cr.set_source_rgb(0.35, 0.35, 0.35)
            cr.arc(x, y, 16, 0, 2 * math.pi); cr.fill()
            cr.set_source_rgb(1, 1, 1); cr.select_font_face("Sans", 0, 0); cr.set_font_size(13)
            label = str(index + 1); ext = cr.text_extents(label)
            cr.move_to(x - ext.width / 2, y + ext.height / 2); cr.show_text(label)

    def _pressed(self, _gesture, _n_press, x, y):
        if self._next >= len(self.POINTS):
            return
        width = max(1, self.canvas.get_width()); height = max(1, self.canvas.get_height())
        px, py = self._point(self._next, width, height)
        if (x - px) ** 2 + (y - py) ** 2 <= 30 ** 2:
            self._connected.append(self._next); self._next += 1
            self.status.set_text("Puzzle complete!" if self._next == len(self.POINTS) else f"Connect dot {self._next + 1}")
            self.canvas.queue_draw()

    def _reset(self, _button):
        self._next = 0; self._connected.clear(); self.status.set_text("Connect dot 1 to begin"); self.canvas.queue_draw()

    def read_file(self, file_path):
        """Restore progress from a Journal object."""
        try:
            payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
            connected = payload.get("connected", []) if isinstance(payload, dict) else []
            if (not isinstance(connected, list) or
                    any(not isinstance(index, int) or index < 0 or index >= len(self.POINTS)
                        for index in connected) or connected != list(range(len(connected)))):
                raise ValueError("invalid connected points")
            self._connected = connected; self._next = len(connected)
            self.status.set_text("Puzzle complete!" if self._next == len(self.POINTS) else f"Connect dot {self._next + 1}")
            self.canvas.queue_draw()
        except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
            self._reset(None)

    def write_file(self, file_path):
        """Persist connected point progress as a Journal object."""
        Path(file_path).write_text(json.dumps({"connected": self._connected}, sort_keys=True) + "\n", encoding="utf-8")
