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

        self.stack = Gtk.DrawingArea()
        self.stack.set_name("org.aspartame.count.stack")
        self.stack.set_size_request(760, 520)
        self.stack.set_hexpand(True)
        self.stack.set_vexpand(True)
        self.stack.set_tooltip_text("Click an empty place to add a box; click a box to remove it. Drag to add several boxes.")
        if aspartame_help:
            aspartame_help.guard(self.stack, "org.aspartame.count.stack")
        self.stack.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                              Gdk.EventMask.BUTTON_RELEASE_MASK |
                              Gdk.EventMask.POINTER_MOTION_MASK)
        self.stack.connect("draw", self._draw_stack)
        self.stack.connect("button-press-event", self._button_press)
        self.stack.connect("button-release-event", self._button_release)
        self.stack.connect("motion-notify-event", self._motion)
        self.root.pack_start(self.stack, True, True, 0)

        self.layer_count = Gtk.Label()
        self.layer_count.set_name("org.aspartame.count.current-layer")
        self.layer_count.get_style_context().add_class("count-layer-count")
        if aspartame_help:
            aspartame_help.guard(self.layer_count, "org.aspartame.count.current-layer")
        self.root.pack_start(self.layer_count, False, False, 0)
        self.layer_total = Gtk.Label()
        self.layer_total.get_style_context().add_class("count-hint")
        self.root.pack_start(self.layer_total, False, False, 0)

        nav = Gtk.Box(spacing=8)
        nav.set_halign(Gtk.Align.CENTER)
        self._symbol_button(nav, "◀", "Move toward the front of the stack.", self._previous_layer,
                            "org.aspartame.count.layer.previous")
        self.layer_position = Gtk.Label()
        self.layer_position.get_style_context().add_class("count-layer-position")
        nav.pack_start(self.layer_position, False, False, 5)
        self._symbol_button(nav, "▶", "Move deeper into the stack.", self._next_layer,
                            "org.aspartame.count.layer.next")
        self.root.pack_start(nav, False, False, 0)

        actions = Gtk.Box(spacing=8)
        actions.set_halign(Gtk.Align.CENTER)
        self._action_button(actions, "＋  New Layer",
                            "Add an empty row behind the deepest row.",
                            self._add_layer, "org.aspartame.count.layer.new")
        self._action_button(actions, "⧉  Copy Layer",
                            "Add a row behind the deepest row with the same boxes as this one.",
                            self._copy_layer, "org.aspartame.count.layer.copy")
        self._make_layer_menu(actions)
        self.root.pack_start(actions, False, False, 0)

        self.set_canvas(self.root)
        self._load()
        self._render()
        self.show_all()

    def _install_style(self):
        css = Gtk.CssProvider()
        css.load_from_data(b"""
            #count-root { background: #eeeeee; color: #222222; }
            #count-title { font-size: 25px; font-weight: bold; }
            .count-total { font-size: 46px; font-weight: bold; }
            .count-hint { font-size: 15px; color: #555555; }
            .count-layer-count { font-size: 19px; font-weight: bold; }
            .count-layer-position { font-size: 18px; font-weight: bold; }
            .count-action { padding: 7px 14px; border-radius: 18px; }
            .count-symbol { min-width: 40px; min-height: 38px; border-radius: 20px; font-size: 20px; }
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
        menu = Gtk.Menu()
        delete = Gtk.MenuItem(label="Delete layer")
        delete.set_name("org.aspartame.count.layer.delete")
        delete.set_tooltip_text("Remove the layer you are looking at.")
        delete.connect("activate", self._delete_layer)
        menu.append(delete)
        menu.show_all()
        more = Gtk.MenuButton()
        more.set_label("⋯")
        more.set_name("org.aspartame.count.layer.more")
        more.set_tooltip_text("More layer actions, including delete layer.")
        more.get_style_context().add_class("count-symbol")
        more.set_popup(menu)
        box.pack_start(more, False, False, 0)

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
        # XY is the front-facing rectangle. Z is a fixed diagonal projection
        # away from the viewer, never a vertical stack.
        size = min(76, (width - 50) / max(1, self.width + len(self.layers) * 0.34),
                   (height - 40) / max(1, self.height + len(self.layers) * 0.22))
        size = max(28, size)
        depth_x, depth_y = size * 0.34, -size * 0.22
        total_width = self.width * size + (len(self.layers) - 1) * depth_x
        total_height = self.height * size + abs((len(self.layers) - 1) * depth_y)
        ox = (width - total_width) / 2
        oy = (height - total_height) / 2 + abs((len(self.layers) - 1) * depth_y)
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
        # Draw deepest rows first. The front row is closest to the viewer.
        order = [i for i in range(len(self.layers) - 1, -1, -1)
                 if i != self.current_layer]
        order.append(self.current_layer)
        for layer_index in order:
            layer = self.layers[layer_index]
            ghost = layer_index != self.current_layer
            distance = abs(layer_index - self.current_layer)
            alpha = max(0.16, 0.34 - distance * 0.035) if ghost else 1.0
            px_offset = layer_index * depth_x
            py_offset = layer_index * depth_y
            for y, row in enumerate(layer):
                for x, occupied in enumerate(row):
                    left = ox + x * size + px_offset
                    top = oy + y * size + py_offset
                    # Every occupied position is a box. The side and top
                    # faces show that later layers are behind, not above.
                    if occupied:
                        cr.set_source_rgba(0.27, 0.27, 0.27, alpha)
                        cr.rectangle(left, top, size - 3, size - 3)
                        cr.fill_preserve()
                        cr.set_source_rgba(0.12, 0.12, 0.12, alpha)
                        cr.set_line_width(1.3)
                        cr.stroke()
                        cr.set_source_rgba(0.42, 0.42, 0.42, alpha)
                        cr.move_to(left, top)
                        cr.line_to(left + depth_x, top + depth_y)
                        cr.line_to(left + size - 3 + depth_x, top + depth_y)
                        cr.line_to(left + size - 3, top)
                        cr.close_path()
                        cr.fill_preserve()
                        cr.stroke()
                        cr.set_source_rgba(0.18, 0.18, 0.18, alpha)
                        cr.move_to(left + size - 3, top)
                        cr.line_to(left + size - 3 + depth_x, top + depth_y)
                        cr.line_to(left + size - 3 + depth_x, top + size - 3 + depth_y)
                        cr.line_to(left + size - 3, top + size - 3)
                        cr.close_path()
                        cr.fill_preserve()
                        cr.stroke()
                    elif layer_index == self.current_layer:
                        cr.set_source_rgba(0.25, 0.25, 0.25, 0.28)
                        cr.rectangle(left, top, size - 3, size - 3)
                        cr.set_line_width(1)
                        cr.stroke()

        # Keep the editable XY plane obvious without covering ghost rows.
        for y in range(self.height):
            for x in range(self.width):
                left = ox + x * size + self.current_layer * depth_x
                top = oy + y * size + self.current_layer * depth_y
                cr.set_source_rgba(0.10, 0.10, 0.10, 0.42)
                cr.rectangle(left, top, size - 3, size - 3)
                cr.set_line_width(1)
                cr.stroke()

    def _hit_cell(self, px, py):
        if len(self.layers) == 1:
            ox, oy, size = self._flat_geometry()
            x, y = int((px - ox) // size), int((py - oy) // size)
            if 0 <= x < self.width and 0 <= y < self.height:
                if ox + x * size <= px <= ox + (x + 1) * size and oy + y * size <= py <= oy + (y + 1) * size:
                    return x, y
            return None
        ox, oy, size, depth_x, depth_y = self._iso_geometry()
        ox += self.current_layer * depth_x
        oy += self.current_layer * depth_y
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
        self._render()

    def _button_press(self, _widget, event):
        cell = self._hit_cell(event.x, event.y)
        self._press_cell = cell
        self._gesture_recorded = False
        self._paint_add = bool(cell is not None and
                               not self.layers[self.current_layer][cell[1]][cell[0]])
        if self._paint_add:
            self._set_cell(cell, True)
        return True

    def _motion(self, _widget, event):
        if self._paint_add and event.state & Gdk.ModifierType.BUTTON1_MASK:
            self._set_cell(self._hit_cell(event.x, event.y), True)
        return True

    def _button_release(self, _widget, event):
        cell = self._hit_cell(event.x, event.y)
        if not self._paint_add and cell == self._press_cell and cell is not None:
            self._set_cell(cell, False)
        self._press_cell = None
        self._paint_add = False
        self._gesture_recorded = False
        return True

    def _add_layer(self, *_):
        self._record()
        self.layers.append(self._empty_layer())
        self.current_layer = len(self.layers) - 1
        self._render()

    def _copy_layer(self, *_):
        self._record()
        copied = json.loads(json.dumps(self.layers[self.current_layer]))
        self.layers.append(copied)
        self.current_layer = len(self.layers) - 1
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
