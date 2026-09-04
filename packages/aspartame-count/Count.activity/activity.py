#!/usr/bin/env python3
import json
import sys

from gi import require_version
require_version("Gdk", "3.0")
require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk

from sugar3.activity import activity
from sugar3.activity.widgets import ActivityToolbarButton, StopButton
from sugar3.graphics.toolbarbox import ToolbarBox

sys.path.insert(0, "/usr/share/aspartame")
try:
    import aspartame_help
except ImportError:
    aspartame_help = None


class CountActivity(activity.Activity):
    """Count boxes on a front face and then look deeper into the stack."""

    def __init__(self, handle):
        super().__init__(handle)
        self.width, self.height = 5, 4
        self.layers = [self._empty_layer()]
        self.current_layer = 0
        self.undo_stack, self.redo_stack = [], []
        self._press_cell = None
        self._paint_add = False
        self._gesture_recorded = False

        toolbar = ToolbarBox()
        toolbar.toolbar.insert(ActivityToolbarButton(self), -1)
        separator = Gtk.SeparatorToolItem()
        separator.set_expand(True)
        toolbar.toolbar.insert(separator, -1)
        toolbar.toolbar.insert(StopButton(self), -1)
        toolbar.show_all()
        self.set_toolbar_box(toolbar)

        self._install_style()
        self.root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.root.set_name("count-root")
        self.root.set_border_width(14)

        title = Gtk.Label(label="Count")
        title.set_name("count-title")
        self.root.pack_start(title, False, False, 0)
        self.total = Gtk.Label()
        self.total.set_name("org.aspartame.count.total")
        self.total.set_tooltip_text("The number of things represented across every layer.")
        if aspartame_help:
            aspartame_help.guard(self.total, "org.aspartame.count.total")
        self.total.get_style_context().add_class("count-total")
        self.root.pack_start(self.total, False, False, 0)
        total_hint = Gtk.Label(label="total")
        total_hint.get_style_context().add_class("count-hint")
        self.root.pack_start(total_hint, False, False, 0)

        content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        content.set_hexpand(True)
        content.set_vexpand(True)
        self.stack = Gtk.DrawingArea()
        self.stack.set_name("org.aspartame.count.stack")
        self.stack.set_size_request(760, 520)
        self.stack.set_hexpand(True)
        self.stack.set_vexpand(True)
        self.stack.set_tooltip_text("Click an empty cell to add a voxel; drag to fill a rectangle. Drag from a voxel to erase a rectangle.")
        if aspartame_help:
            aspartame_help.guard(self.stack, "org.aspartame.count.stack")
        self.stack.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                              Gdk.EventMask.BUTTON_RELEASE_MASK |
                              Gdk.EventMask.POINTER_MOTION_MASK)
        self.stack.connect("draw", self._draw_stack)
        self.stack.connect("button-press-event", self._button_press)
        self.stack.connect("button-release-event", self._button_release)
        self.stack.connect("motion-notify-event", self._motion)
        content.pack_start(self.stack, True, True, 0)

        rail = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        rail.set_size_request(190, -1)
        rail.set_valign(Gtk.Align.CENTER)
        rail.get_style_context().add_class("count-rail")
        layer_heading = Gtk.Label(label="EDIT LAYER")
        layer_heading.get_style_context().add_class("count-rail-heading")
        rail.pack_start(layer_heading, False, False, 0)
        self.layer_count = Gtk.Label()
        self.layer_count.set_name("org.aspartame.count.current-layer")
        self.layer_count.get_style_context().add_class("count-layer-count")
        if aspartame_help:
            aspartame_help.guard(self.layer_count, "org.aspartame.count.current-layer")
        rail.pack_start(self.layer_count, False, False, 0)
        self.layer_total = Gtk.Label()
        self.layer_total.get_style_context().add_class("count-hint")
        rail.pack_start(self.layer_total, False, False, 0)

        self._symbol_button(rail, "↑  Back layer", "Select the adjacent layer behind this one.",
                            self._previous_layer, "org.aspartame.count.layer.previous")
        self._symbol_button(rail, "↓  Forward layer", "Select the adjacent layer in front of this one.",
                            self._next_layer, "org.aspartame.count.layer.next")
        self.layer_position = Gtk.Label()
        self.layer_position.get_style_context().add_class("count-layer-position")
        rail.pack_start(self.layer_position, False, False, 0)
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        rail.pack_start(separator, False, False, 4)
        self._action_button(rail, "＋  New layer", "Add an empty layer behind the selected layer.",
                            self._add_layer, "org.aspartame.count.layer.new")
        self._action_button(rail, "⧉  Copy layer", "Copy the selected layer behind it.",
                            self._copy_layer, "org.aspartame.count.layer.copy")
        self._make_layer_menu(rail)
        content.pack_start(rail, False, False, 0)
        self.root.pack_start(content, True, True, 0)

        self.set_canvas(self.root)
        self._load()
        self._render()
        self.show_all()

    def _install_style(self):
        css = Gtk.CssProvider()
        css.load_from_data(b"""
            #count-root { background: #f4f6f7; color: #18232b; }
            #count-title { font-size: 25px; font-weight: bold; }
            .count-total { font-size: 46px; font-weight: bold; color: #1b668f; }
            .count-hint { font-size: 14px; color: #52616b; }
            .count-rail { background: #e3ebef; border: 1px solid #a8bac4; border-radius: 16px; padding: 14px; }
            .count-rail-heading { font-size: 12px; letter-spacing: 1px; color: #52616b; }
            .count-layer-count { font-size: 20px; font-weight: bold; color: #173f55; }
            .count-layer-position { font-size: 18px; font-weight: bold; color: #1b668f; padding: 4px; }
            .count-action { padding: 8px 12px; border-radius: 18px; }
            .count-symbol { min-width: 40px; min-height: 38px; border-radius: 19px; font-size: 15px; }
        """)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _empty_layer(self):
        return [[False for _ in range(self.width)] for _ in range(self.height)]

    def _symbol_button(self, box, label, tooltip, callback, name):
        button = Gtk.Button(label=label)
        button.set_name(name)
        button.set_tooltip_text(tooltip)
        button.get_style_context().add_class("count-symbol")
        button.connect("clicked", callback)
        if aspartame_help:
            aspartame_help.guard(button, name)
        box.pack_start(button, False, False, 0)
        return button

    def _action_button(self, box, label, tooltip, callback, name):
        button = Gtk.Button(label=label)
        button.set_name(name)
        button.set_tooltip_text(tooltip)
        button.get_style_context().add_class("count-action")
        button.connect("clicked", callback)
        if aspartame_help:
            aspartame_help.guard(button, name)
        box.pack_start(button, False, False, 0)
        return button

    def _make_layer_menu(self, box):
        # Deleting the selected layer is a single, visible action.  There is no
        # intermediate overflow menu between the user's intent and the result.
        self._action_button(box, "Delete layer", "Remove the selected layer.",
                            self._delete_layer, "org.aspartame.count.layer.delete")

    def _snapshot(self):
        return {"width": self.width, "height": self.height,
                "layers": self.layers, "current_layer": self.current_layer}

    def _record(self):
        self.undo_stack.append(json.loads(json.dumps(self._snapshot())))
        self.redo_stack.clear()

    def _layer_count(self, layer):
        return sum(sum(row) for row in layer)

    def _render(self):
        total = sum(self._layer_count(layer) for layer in self.layers)
        current = self._layer_count(self.layers[self.current_layer])
        self.total.set_text(str(total))
        self.layer_count.set_text("Layer %d of %d" %
                                  (self.current_layer + 1, len(self.layers)))
        self.layer_total.set_text("%d on this layer" % current)
        self.layer_position.set_text("%d / %d" %
                                     (self.current_layer + 1, len(self.layers)))
        self.stack.queue_draw()

    def _flat_geometry(self):
        width = max(1, self.stack.get_allocated_width())
        height = max(1, self.stack.get_allocated_height())
        size = min(88, (width - 36) / self.width, (height - 36) / self.height)
        size = max(28, size)
        ox = (width - self.width * size) / 2
        oy = (height - self.height * size) / 2
        return ox, oy, size

    def _iso_geometry(self):
        width = max(1, self.stack.get_allocated_width())
        height = max(1, self.stack.get_allocated_height())
        size = min(100, (width - 100) / max(1, self.width + len(self.layers) * 0.12),
                   (height - 80) / max(1, self.height + len(self.layers) * 0.08))
        size = max(28, size)
        depth_x, depth_y = size * 0.30, -size * 0.20
        relatives = range(-self.current_layer, len(self.layers) - self.current_layer)
        min_x, max_x = min(relatives) * depth_x, max(relatives) * depth_x
        min_y, max_y = min(relatives) * depth_y, max(relatives) * depth_y
        total_width = self.width * size + max_x - min_x
        total_height = self.height * size + max_y - min_y
        ox = (width - total_width) / 2 - min_x
        oy = (height - total_height) / 2 - min_y
        # Cells in one layer stay aligned; the shallow offset is only between
        # layers, preserving a readable 3D stack without a staircase grid.
        return ox, oy, size, depth_x, depth_y

    def _draw_stack(self, widget, cr):
        if len(self.layers) == 1:
            self._draw_front_face(cr)
        else:
            self._draw_depth_stack(cr)
        return False

    def _draw_front_face(self, cr):
        ox, oy, size = self._flat_geometry()
        layer = self.layers[0]
        for y in range(self.height):
            for x in range(self.width):
                left, top = ox + x * size, oy + y * size
                cr.set_source_rgb(0.27, 0.27, 0.27) if layer[y][x] else cr.set_source_rgb(1, 1, 1)
                cr.rectangle(left, top, size - 3, size - 3)
                cr.fill_preserve()
                cr.set_source_rgb(0.43, 0.43, 0.43)
                cr.set_line_width(2)
                cr.stroke()

    def _draw_depth_stack(self, cr):
        ox, oy, size, depth_x, depth_y = self._iso_geometry()
        # Draw each plane's sparse grid first.  The selected plane is blue and
        # strong; rear planes are readable context, while front planes barely
        # veil the selected work surface.
        order = (list(range(len(self.layers) - 1, self.current_layer, -1)) +
                 [self.current_layer] + list(range(self.current_layer - 1, -1, -1)))
        for layer_index in order:
            relative = layer_index - self.current_layer
            distance = abs(relative)
            selected = relative == 0
            if selected:
                grid_alpha = 0.72
            elif relative > 0:       # behind the selected plane
                grid_alpha = max(0.26, 0.38 - distance * 0.025)
            else:                    # in front of the selected plane
                grid_alpha = max(0.18, 0.24 - distance * 0.012)
            px_offset, py_offset = relative * depth_x, relative * depth_y
            cr.set_source_rgba(0.12, 0.40, 0.62, grid_alpha)
            cr.set_line_width(2.0 if selected else 1.0)
            # One continuous grid per plane: no inset rectangles or extra
            # outlines that make the grid look denser than the actual model.
            for x in range(self.width + 1):
                xx = ox + x * size + px_offset
                cr.move_to(xx, oy + py_offset)
                cr.line_to(xx, oy + self.height * size + py_offset)
            for y in range(self.height + 1):
                yy = oy + y * size + py_offset
                cr.move_to(ox + px_offset, yy)
                cr.line_to(ox + self.width * size + px_offset, yy)
            cr.stroke()

            layer = self.layers[layer_index]
            cube_alpha = 1.0 if selected else (max(0.30, 0.50 - distance * 0.04)
                                               if relative > 0 else max(0.24, 0.34 - distance * 0.018))
            for y, row in enumerate(layer):
                for x, occupied in enumerate(row):
                    if not occupied:
                        continue
                    left = ox + x * size + px_offset
                    top = oy + y * size + py_offset
                    cr.set_source_rgba(0.42, 0.45, 0.47, cube_alpha)
                    cr.rectangle(left + 1, top + 1, size - 3, size - 3)
                    cr.fill_preserve()
                    cr.set_source_rgba(0.20, 0.22, 0.23, cube_alpha)
                    cr.set_line_width(2.2 if selected else 1.1)
                    cr.stroke()
                    cr.set_source_rgba(0.64, 0.66, 0.67, cube_alpha)
                    cr.move_to(left + 1, top + 1)
                    cr.line_to(left + 1 + depth_x, top + 1 + depth_y)
                    cr.line_to(left + size - 2 + depth_x, top + 1 + depth_y)
                    cr.line_to(left + size - 2, top + 1)
                    cr.close_path()
                    cr.fill_preserve()
                    cr.stroke()
                    cr.set_source_rgba(0.25, 0.26, 0.27, cube_alpha)
                    cr.move_to(left + size - 2, top + 1)
                    cr.line_to(left + size - 2 + depth_x, top + 1 + depth_y)
                    cr.line_to(left + size - 2 + depth_x, top + size - 2 + depth_y)
                    cr.line_to(left + size - 2, top + size - 2)
                    cr.close_path()
                    cr.fill_preserve()
                    cr.stroke()

    def _hit_cell(self, px, py):
        if len(self.layers) == 1:
            ox, oy, size = self._flat_geometry()
        else:
            ox, oy, size, depth_x, depth_y = self._iso_geometry()
            ox += 0
            oy += 0
        x, y = int((px - ox) // size), int((py - oy) // size)
        if 0 <= x < self.width and 0 <= y < self.height:
            if ox + x * size <= px <= ox + (x + 1) * size and oy + y * size <= py <= oy + (y + 1) * size:
                return x, y
        return None

    def _set_cell(self, cell, value):
        if cell is None:
            return
        x, y = cell
        if self.layers[self.current_layer][y][x] == value:
            return
        if not self._gesture_recorded:
            self._record()
            self._gesture_recorded = True
        self.layers[self.current_layer][y][x] = value

    def _apply_rectangle(self, end_cell):
        if self._press_cell is None or end_cell is None:
            return
        x0, y0 = self._press_cell
        x1, y1 = end_cell
        changed = False
        for y in range(min(y0, y1), max(y0, y1) + 1):
            for x in range(min(x0, x1), max(x0, x1) + 1):
                if self.layers[self.current_layer][y][x] != self._paint_add:
                    if not self._gesture_recorded:
                        self._record()
                        self._gesture_recorded = True
                    self.layers[self.current_layer][y][x] = self._paint_add
                    changed = True
        if changed:
            self._render()

    def _button_press(self, _widget, event):
        self._press_cell = self._hit_cell(event.x, event.y)
        self._gesture_recorded = False
        if self._press_cell is not None:
            x, y = self._press_cell
            self._paint_add = not self.layers[self.current_layer][y][x]
            self._apply_rectangle(self._press_cell)
        return True

    def _motion(self, _widget, event):
        if self._press_cell is not None and event.state & Gdk.ModifierType.BUTTON1_MASK:
            self._apply_rectangle(self._hit_cell(event.x, event.y))
        return True

    def _button_release(self, _widget, event):
        self._apply_rectangle(self._hit_cell(event.x, event.y))
        self._press_cell = None
        self._paint_add = False
        self._gesture_recorded = False
        return True

    def _add_layer(self, *_):
        self._record()
        # Insert depth behind the plane being edited; keep that plane selected
        # so the new translucent context is immediately visible.
        self.layers.insert(self.current_layer + 1, self._empty_layer())
        self._render()

    def _copy_layer(self, *_):
        self._record()
        copied = json.loads(json.dumps(self.layers[self.current_layer]))
        self.layers.insert(self.current_layer + 1, copied)
        self._render()

    def _delete_layer(self, *_):
        if len(self.layers) == 1:
            return
        self._record()
        self.layers.pop(self.current_layer)
        self.current_layer = min(self.current_layer, len(self.layers) - 1)
        self._render()

    def _previous_layer(self, *_):
        if self.current_layer > 0:
            self.current_layer -= 1
            self._render()

    def _next_layer(self, *_):
        if self.current_layer + 1 < len(self.layers):
            self.current_layer += 1
            self._render()

    def write_file(self, file_path):
        with open(file_path, "w", encoding="utf-8") as stream:
            json.dump(self._snapshot(), stream)

    def read_file(self, file_path):
        with open(file_path, encoding="utf-8") as stream:
            state = json.load(stream)
        self.width = int(state["width"])
        self.height = int(state["height"])
        self.layers = state["layers"]
        self.current_layer = min(int(state.get("current_layer", 0)), len(self.layers) - 1)
        self._render()

    def _load(self):
        return
