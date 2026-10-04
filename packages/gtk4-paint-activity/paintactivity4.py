"""Native GTK4 Paint activity.

The canvas keeps its model in Python (each mark is a tool, a colour, a width,
and points), so pointer input and rendering stay independent of GTK widgets.

Tools: pencil, line, rectangle, ellipse, and eraser, with four brush sizes, a
palette plus a custom colour chooser, undo/redo (Ctrl+Z / Ctrl+Shift+Z; Clear
is undoable), and PNG export.  Text, fill bucket, image import, layers, and
collaboration from GTK3 Paint remain unported.

Journal payload history (append-only):

* v1: ``{"color": name, "strokes": [{"color": name, "points": [[x, y]...]}]}``
* 2026-10-02: strokes may add ``"tool"`` and ``"width"``; colours may be
  ``"#rrggbb"``; the top level adds ``"tool"`` and ``"width"``.  Missing fields
  mean pencil and width 5, so v1 drawings load unchanged.
"""

import json
import math
import re
from pathlib import Path

from gi.repository import Gdk, Gio, GLib, Gtk
from sugar4.activity import SimpleActivity


TOOLS = ("pencil", "line", "rectangle", "ellipse", "eraser")
TOOL_LABELS = {"pencil": "Pencil", "line": "Line", "rectangle": "Rectangle",
               "ellipse": "Ellipse", "eraser": "Eraser"}
WIDTHS = (2, 5, 10, 20)
DEFAULT_WIDTH = 5
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


class PaintActivity(SimpleActivity):
    COLORS = {
        "Black": (0.05, 0.05, 0.05),
        "Red": (0.85, 0.12, 0.12),
        "Blue": (0.08, 0.30, 0.80),
        "Yellow": (0.95, 0.70, 0.05),
        "Green": (0.15, 0.62, 0.25),
        "Orange": (0.95, 0.48, 0.10),
        "Purple": (0.52, 0.22, 0.68),
        "Brown": (0.48, 0.30, 0.15),
    }

    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Paint")
        self.color = "Black"
        self.tool = "pencil"
        self.width = DEFAULT_WIDTH
        self.strokes = []
        self._undo, self._redo = [], []
        self._active_stroke = None
        self._build()

    # -- interface -----------------------------------------------------

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        root.set_margin_top(24); root.set_margin_bottom(24)
        root.set_margin_start(30); root.set_margin_end(30)
        root.set_hexpand(True)
        root.set_vexpand(True)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Paint activity"])

        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        body.set_hexpand(True)
        body.set_vexpand(True)
        body.set_halign(Gtk.Align.FILL)
        body.set_valign(Gtk.Align.FILL)
        root.append(body)

        title = Gtk.Label(label="Paint", xalign=0)
        title.add_css_class("title-1")
        body.append(title)

        tools = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        tools.update_property([Gtk.AccessibleProperty.LABEL], ["Drawing tools"])
        self.tool_buttons = {}
        group = None
        for tool in TOOLS:
            button = Gtk.ToggleButton(label=TOOL_LABELS[tool])
            button.update_property([Gtk.AccessibleProperty.LABEL], ["%s tool" % TOOL_LABELS[tool]])
            if group is not None:
                button.set_group(group)
            group = group or button
            button.connect("toggled", self._tool_toggled, tool)
            self.tool_buttons[tool] = button
            tools.append(button)
        tools.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        self.width_choice = Gtk.DropDown.new_from_strings(["Fine", "Medium", "Thick", "Huge"])
        self.width_choice.set_selected(WIDTHS.index(DEFAULT_WIDTH))
        self.width_choice.set_tooltip_text("Brush size")
        self.width_choice.update_property([Gtk.AccessibleProperty.LABEL], ["Brush size"])
        self.width_choice.connect("notify::selected", self._width_chosen)
        tools.append(self.width_choice)
        tools.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        for label, tip, callback in (("Undo", "Undo (Ctrl+Z)", self._do_undo),
                                     ("Redo", "Redo (Ctrl+Shift+Z)", self._do_redo),
                                     ("Save PNG", "Export the picture as a PNG image", self._export)):
            button = Gtk.Button(label=label)
            button.set_tooltip_text(tip)
            button.update_property([Gtk.AccessibleProperty.LABEL], [tip.split(" (")[0]])
            button.connect("clicked", lambda _b, cb=callback: cb())
            tools.append(button)
        body.append(tools)

        self._drawing_area = Gtk.DrawingArea()
        self._drawing_area.set_content_width(720)
        self._drawing_area.set_content_height(440)
        self._drawing_area.set_hexpand(True)
        self._drawing_area.set_vexpand(True)
        self._drawing_area.set_draw_func(self._draw)
        self._drawing_area.update_property(
            [Gtk.AccessibleProperty.LABEL, Gtk.AccessibleProperty.DESCRIPTION],
            ["Drawing canvas", "Drag the pointer across the canvas to draw"],
        )
        drag = Gtk.GestureDrag()
        drag.set_button(1)
        drag.connect("drag-begin", self._drag_begin)
        drag.connect("drag-update", self._drag_update)
        drag.connect("drag-end", self._drag_end)
        self._drawing_area.add_controller(drag)
        canvas_frame = Gtk.Frame(label="Drawing canvas")
        canvas_frame.set_hexpand(True)
        canvas_frame.set_vexpand(True)
        canvas_frame.set_child(self._drawing_area)
        body.append(canvas_frame)

        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        controls.update_property([Gtk.AccessibleProperty.LABEL], ["Paint controls"])
        for name in self.COLORS:
            button = Gtk.Button(label=name)
            button.update_property([Gtk.AccessibleProperty.LABEL], [f"Use {name} ink"])
            button.connect("clicked", self._choose_color, name)
            controls.append(button)
        if hasattr(Gtk, "ColorDialogButton"):
            self.custom = Gtk.ColorDialogButton(dialog=Gtk.ColorDialog(with_alpha=False))
            self.custom.set_tooltip_text("Choose any colour")
            self.custom.update_property([Gtk.AccessibleProperty.LABEL], ["Choose any colour"])
            self.custom.connect("notify::rgba", self._custom_color)
            controls.append(self.custom)
        clear = Gtk.Button(label="Clear")
        clear.update_property([Gtk.AccessibleProperty.LABEL], ["Clear drawing"])
        clear.connect("clicked", self._clear)
        controls.append(clear)
        body.append(controls)
        self.status = Gtk.Label(xalign=0)
        self.status.add_css_class("dim-label")
        self.status.update_property([Gtk.AccessibleProperty.LABEL], ["Drawing status"])
        body.append(self.status)
        self.set_canvas(root)
        self._install_shortcuts(root)
        self.tool_buttons["pencil"].set_active(True)
        self._update_status()

        provider = Gtk.CssProvider()
        provider.load_from_data(
            b"frame { border: 2px solid #8aa8b8; border-radius: 8px; padding: 8px; } "
            b"drawingarea { background: #ffffff; } "
            b"button { min-height: 42px; border-radius: 19px; }"
        )
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    def _install_shortcuts(self, widget):
        controller = Gtk.ShortcutController()
        controller.set_scope(Gtk.ShortcutScope.MANAGED)
        for accel, callback in (("<Control>z", self._do_undo), ("<Control><Shift>z", self._do_redo),
                                ("<Control>y", self._do_redo)):
            action = Gtk.CallbackAction.new(lambda *_a, cb=callback: (cb(), True)[1])
            controller.add_shortcut(Gtk.Shortcut.new(Gtk.ShortcutTrigger.parse_string(accel), action))
        widget.add_controller(controller)

    def _update_status(self):
        verb = "drag to erase" if self.tool == "eraser" else "drag to draw"
        self.status.set_text(f"{self.color} ink · {TOOL_LABELS[self.tool]} · {verb}")

    def _rgb(self, color):
        if color in self.COLORS:
            return self.COLORS[color]
        if isinstance(color, str) and HEX.match(color):
            return tuple(int(color[i:i + 2], 16) / 255 for i in (1, 3, 5))
        return self.COLORS["Black"]

    # -- input ---------------------------------------------------------

    def _tool_toggled(self, button, tool):
        if button.get_active():
            self.tool = tool
            self._update_status()

    def _width_chosen(self, dropdown, _pspec):
        self.width = WIDTHS[dropdown.get_selected()]

    def _drag_begin(self, _gesture, x, y):
        self._active_stroke = [self.color, [(x, y)], self.tool, self.width]
        self._push_undo()
        self.strokes.append(self._active_stroke)
        self._drawing_area.queue_draw()

    def _drag_update(self, gesture, offset_x, offset_y):
        if self._active_stroke is None:
            return
        start_x, start_y = gesture.get_start_point()
        point = (start_x + offset_x, start_y + offset_y)
        if self._active_stroke[2] in ("pencil", "eraser"):
            self._active_stroke[1].append(point)
        else:
            # Shapes keep only their two defining corners.
            self._active_stroke[1][1:] = [point]
        self._drawing_area.queue_draw()

    def _drag_end(self, _gesture, _offset_x, _offset_y):
        self._active_stroke = None

    def _choose_color(self, _button, name):
        self.color = name
        if self.tool == "eraser":
            self.tool_buttons["pencil"].set_active(True)
        self._update_status()

    def _custom_color(self, button, _pspec):
        rgba = button.get_rgba()
        self.color = "#%02x%02x%02x" % tuple(round(c * 255) for c in (rgba.red, rgba.green, rgba.blue))
        self._update_status()

    # -- history -------------------------------------------------------

    def _snapshot(self):
        return [[s[0], list(s[1]), s[2], s[3]] for s in self.strokes]

    def _push_undo(self):
        self._undo.append(self._snapshot())
        del self._undo[:-100]
        self._redo.clear()

    def _do_undo(self):
        if self._undo:
            self._redo.append(self._snapshot())
            self.strokes = self._undo.pop()
            self._drawing_area.queue_draw()

    def _do_redo(self):
        if self._redo:
            self._undo.append(self._snapshot())
            self.strokes = self._redo.pop()
            self._drawing_area.queue_draw()

    def _clear(self, _button):
        if self.strokes:
            self._push_undo()
        self.strokes = []
        self._update_status()
        self.status.set_text(self.status.get_text() + " · cleared (Undo brings it back)")
        self._drawing_area.queue_draw()

    # -- drawing -------------------------------------------------------

    def _draw(self, _area, cr, width, height):
        cr.set_source_rgb(1, 1, 1)
        cr.paint()
        self._paint_strokes(cr)

    def _paint_strokes(self, cr):
        cr.set_line_cap(1)  # round
        cr.set_line_join(1)
        for color, points, tool, line_width in self.strokes:
            if not points:
                continue
            cr.set_line_width(line_width)
            cr.set_source_rgb(*((1, 1, 1) if tool == "eraser" else self._rgb(color)))
            if tool in ("pencil", "eraser") or len(points) == 1:
                cr.move_to(*points[0])
                for point in points[1:]:
                    cr.line_to(*point)
                if len(points) == 1:
                    cr.arc(points[0][0], points[0][1], line_width / 2, 0, 2 * math.pi)
                    cr.fill()
                else:
                    cr.stroke()
                continue
            (x0, y0), (x1, y1) = points[0], points[-1]
            if tool == "line":
                cr.move_to(x0, y0); cr.line_to(x1, y1)
            elif tool == "rectangle":
                cr.rectangle(min(x0, x1), min(y0, y1), abs(x1 - x0), abs(y1 - y0))
            elif tool == "ellipse":
                cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
                rx, ry = max(abs(x1 - x0) / 2, 0.5), max(abs(y1 - y0) / 2, 0.5)
                cr.save(); cr.translate(cx, cy); cr.scale(rx, ry)
                cr.arc(0, 0, 1, 0, 2 * math.pi); cr.restore()
            cr.stroke()

    def _export(self):
        dialog = Gtk.FileDialog(title="Save the picture as PNG")
        dialog.set_initial_name("painting.png")
        dialog.save(self, None, self._export_chosen)

    def render_png(self, path):
        import cairo
        width = max(1, self._drawing_area.get_width() or 720)
        height = max(1, self._drawing_area.get_height() or 440)
        surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
        cr = cairo.Context(surface)
        cr.set_source_rgb(1, 1, 1); cr.paint()
        self._paint_strokes(cr)
        surface.write_to_png(path)

    def _export_chosen(self, dialog, result):
        try:
            target = dialog.save_finish(result)
        except GLib.Error:
            return
        if target is None or target.get_path() is None:
            return
        try:
            self.render_png(target.get_path())
        except (OSError, ImportError) as error:
            self.status.set_text("Could not save the picture: %s" % error)
            return
        self.status.set_text("Saved %s" % target.get_basename())

    # -- Journal -------------------------------------------------------

    def _valid_color(self, color):
        return color in self.COLORS or (isinstance(color, str) and bool(HEX.match(color)))

    def read_file(self, file_path):
        """Restore tool, colour, and marks from a JSON Journal object."""
        try:
            payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("payload must be an object")
            color = payload.get("color", "Black")
            strokes = payload.get("strokes", [])
            if not self._valid_color(color) or not isinstance(strokes, list):
                raise ValueError("invalid drawing")
            restored = []
            for stroke in strokes:
                if not isinstance(stroke, dict) or not self._valid_color(stroke.get("color")):
                    continue
                tool = stroke.get("tool", "pencil")
                tool = tool if tool in TOOLS else "pencil"
                line_width = stroke.get("width", DEFAULT_WIDTH)
                line_width = line_width if isinstance(line_width, (int, float)) and 0 < line_width <= 100 else DEFAULT_WIDTH
                points = [tuple(point) for point in stroke.get("points", [])
                          if isinstance(point, list) and len(point) == 2
                          and all(isinstance(v, (int, float)) for v in point)]
                if points:
                    restored.append([stroke["color"], points, tool, line_width])
            tool = payload.get("tool", "pencil")
            width = payload.get("width", DEFAULT_WIDTH)
        except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
            color, restored, tool, width = "Black", [], "pencil", DEFAULT_WIDTH
        self.color = color
        self.strokes = restored
        self._undo.clear(); self._redo.clear()
        self.tool_buttons[tool if tool in TOOLS else "pencil"].set_active(True)
        if width in WIDTHS:
            self.width_choice.set_selected(WIDTHS.index(width))
        self._update_status()
        self._drawing_area.queue_draw()

    def write_file(self, file_path):
        """Save tool, colour, and marks as a JSON Journal object."""
        payload = {"color": self.color, "tool": self.tool, "width": self.width,
                   "strokes": [{"color": color, "points": points, "tool": tool, "width": line_width}
                               for color, points, tool, line_width in self.strokes]}
        Path(file_path).write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
