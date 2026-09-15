"""Small native GTK4 Paint activity.

The canvas deliberately keeps its model in Python (strokes are lists of
points), so pointer input and rendering remain independent of GTK widgets.
"""

import json
from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class PaintActivity(SimpleActivity):
    COLORS = {
        "Black": (0.05, 0.05, 0.05),
        "Red": (0.85, 0.12, 0.12),
        "Blue": (0.08, 0.30, 0.80),
        "Yellow": (0.95, 0.70, 0.05),
    }

    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Paint")
        self.color = "Black"
        self.strokes = []
        self._active_stroke = None
        self._build()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        root.set_margin_top(24)
        root.set_margin_bottom(24)
        root.set_margin_start(30)
        root.set_margin_end(30)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Paint activity"])

        title = Gtk.Label(label="Paint", xalign=0)
        title.add_css_class("title-1")
        root.append(title)

        self.canvas = Gtk.DrawingArea()
        self.canvas.set_content_width(720)
        self.canvas.set_content_height(440)
        self.canvas.set_hexpand(True)
        self.canvas.set_vexpand(True)
        self.canvas.set_draw_func(self._draw)
        self.canvas.update_property(
            [Gtk.AccessibleProperty.LABEL, Gtk.AccessibleProperty.DESCRIPTION],
            ["Drawing canvas", "Drag the pointer across the canvas to draw"],
        )
        drag = Gtk.GestureDrag()
        drag.set_button(1)
        drag.connect("drag-begin", self._drag_begin)
        drag.connect("drag-update", self._drag_update)
        drag.connect("drag-end", self._drag_end)
        self.canvas.add_controller(drag)
        root.append(self.canvas)

        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        controls.update_property([Gtk.AccessibleProperty.LABEL], ["Paint controls"])
        for name in self.COLORS:
            button = Gtk.Button(label=name)
            button.update_property([Gtk.AccessibleProperty.LABEL], [f"Use {name} ink"])
            button.connect("clicked", self._choose_color, name)
            controls.append(button)
        clear = Gtk.Button(label="Clear")
        clear.update_property([Gtk.AccessibleProperty.LABEL], ["Clear drawing"])
        clear.connect("clicked", self._clear)
        controls.append(clear)
        root.append(controls)
        self.status = Gtk.Label(label="Black ink · drag to draw", xalign=0)
        self.status.add_css_class("dim-label")
        self.status.update_property([Gtk.AccessibleProperty.LABEL], ["Drawing status"])
        root.append(self.status)
        self.set_canvas(root)

        provider = Gtk.CssProvider()
        provider.load_from_data(
            b"drawingarea { background: #ffffff; border: 2px solid #8aa8b8; } "
            b"button { min-height: 42px; border-radius: 19px; }"
        )
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    def _drag_begin(self, _gesture, x, y):
        self._active_stroke = [self.color, [(x, y)]]
        self.strokes.append(self._active_stroke)
        self.canvas.queue_draw()

    def _drag_update(self, gesture, offset_x, offset_y):
        if self._active_stroke is None:
            return
        start_x, start_y = gesture.get_start_point()
        self._active_stroke[1].append((start_x + offset_x, start_y + offset_y))
        self.canvas.queue_draw()

    def _drag_end(self, _gesture, _offset_x, _offset_y):
        self._active_stroke = None

    def _choose_color(self, _button, name):
        self.color = name
        self.status.set_text(f"{name} ink · drag to draw")

    def _clear(self, _button):
        self.strokes.clear()
        self.status.set_text(f"{self.color} ink · drag to draw")
        self.canvas.queue_draw()

    def _draw(self, _area, cr, width, height):
        cr.set_source_rgb(1, 1, 1)
        cr.paint()
        cr.set_line_width(5)
        cr.set_line_cap(1)  # round
        cr.set_line_join(1)
        for name, points in self.strokes:
            if not points:
                continue
            cr.set_source_rgb(*self.COLORS[name])
            cr.move_to(*points[0])
            for point in points[1:]:
                cr.line_to(*point)
            if len(points) == 1:
                cr.arc(points[0][0], points[0][1], 2.5, 0, 6.283185)
                cr.fill()
            else:
                cr.stroke()

    def read_file(self, file_path):
        """Restore color and stroke geometry from a JSON Journal object."""
        try:
            payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("payload must be an object")
            color = payload.get("color", "Black")
            strokes = payload.get("strokes", [])
            if color not in self.COLORS or not isinstance(strokes, list):
                raise ValueError("invalid drawing")
            restored = []
            for stroke in strokes:
                if not isinstance(stroke, dict) or stroke.get("color") not in self.COLORS:
                    continue
                points = [tuple(point) for point in stroke.get("points", []) if isinstance(point, list) and len(point) == 2]
                if points:
                    restored.append([stroke["color"], points])
        except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
            color, restored = "Black", []
        self.color = color
        self.strokes = restored
        self.status.set_text(f"{self.color} ink · drag to draw")
        self.canvas.queue_draw()

    def write_file(self, file_path):
        """Save color and stroke geometry as a JSON Journal object."""
        payload = {"color": self.color, "strokes": [{"color": color, "points": points} for color, points in self.strokes]}
        Path(file_path).write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
