#!/usr/bin/env python3
import json

from gi import require_version
require_version("Gdk", "3.0")
require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk

from sugar3.activity import activity
from sugar3.activity.widgets import ActivityToolbarButton, StopButton
from sugar3.graphics.toolbarbox import ToolbarBox


class CountActivity(activity.Activity):
    """Simple cell counting with optional numbered layers."""

    def __init__(self, handle):
        super().__init__(handle)
        self.width, self.height = 5, 4
        self.layers = [self._empty_layer()]
        self.current_layer = 0
        self.undo_stack, self.redo_stack = [], []

        toolbar = ToolbarBox()
        toolbar.toolbar.insert(ActivityToolbarButton(self), -1)
        separator = Gtk.SeparatorToolItem()
        separator.set_expand(True)
        toolbar.toolbar.insert(separator, -1)
        toolbar.toolbar.insert(StopButton(self), -1)
        toolbar.show_all()
        self.set_toolbar_box(toolbar)

        self._install_style()
        self.root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.root.set_name("count-root")
        self.root.set_border_width(18)

        heading = Gtk.Label(label="Count")
        heading.set_name("count-title")
        self.root.pack_start(heading, False, False, 0)

        self.summary = Gtk.Label()
        self.summary.set_name("count-summary")
        self.root.pack_start(self.summary, False, False, 0)

        self.content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=18)
        self.content.set_halign(Gtk.Align.CENTER)
        self.content.set_valign(Gtk.Align.CENTER)
        self.root.pack_start(self.content, True, True, 0)

        self.grid = Gtk.Grid(row_spacing=4, column_spacing=4)
        self.grid.set_halign(Gtk.Align.CENTER)
        self.grid.set_valign(Gtk.Align.CENTER)
        self.content.pack_start(self.grid, False, False, 0)

        self.total_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.total_box.set_valign(Gtk.Align.CENTER)
        self.total = Gtk.Label()
        self.total.set_name("count-total")
        self.total_box.pack_start(self.total, False, False, 0)
        self.total_hint = Gtk.Label(label="filled cells")
        self.total_hint.set_name("count-hint")
        self.total_box.pack_start(self.total_hint, False, False, 0)
        self.content.pack_start(self.total_box, False, False, 0)

        self.voxels = Gtk.DrawingArea()
        self.voxels.set_size_request(360, 300)
        self.voxels.connect("draw", self._draw_voxels)
        self.voxels.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.voxels.connect("button-press-event", self._voxel_clicked)

        self.actions = Gtk.Box(spacing=8)
        self.actions.set_halign(Gtk.Align.CENTER)
        self._pill(self.actions, "Previous layer", self._previous_layer)
        self._pill(self.actions, "Next layer", self._next_layer)
        self._pill(self.actions, "Add layer", self._add_layer)
        self._pill(self.actions, "Copy layer", self._copy_layer)
        self._pill(self.actions, "Delete layer", self._delete_layer)
        self.root.pack_start(self.actions, False, False, 0)

        self.set_canvas(self.root)
        self._load()
        self._render()
        self.show_all()

    def _install_style(self):
        css = Gtk.CssProvider()
        css.load_from_data(b"""
            #count-root { background: #eeeeee; color: #222222; }
            #count-title { font-size: 26px; font-weight: bold; }
            #count-summary { font-size: 16px; }
            #count-total { font-size: 42px; font-weight: bold; }
            #count-hint { font-size: 15px; color: #555555; }
            .count-cell { min-width: 68px; min-height: 68px; background: #ffffff;
                          border: 2px solid #777777; border-radius: 5px;
                          color: #444444; font-size: 22px; }
            .count-cell:checked { background: #444444; color: #ffffff; }
            .count-pill { padding: 7px 13px; border-radius: 18px; }
        """)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _empty_layer(self):
        return [[False for _ in range(self.width)] for _ in range(self.height)]

    def _pill(self, box, label, callback):
        button = Gtk.Button(label=label)
        button.get_style_context().add_class("count-pill")
        button.connect("clicked", callback)
        box.pack_start(button, False, False, 0)
        return button

    def _snapshot(self):
        return {"width": self.width, "height": self.height,
                "layers": self.layers, "current_layer": self.current_layer}

    def _record(self):
        self.undo_stack.append(json.loads(json.dumps(self._snapshot())))
        self.redo_stack.clear()

    def _render(self):
        for child in self.grid.get_children():
            self.grid.remove(child)
        layer = self.layers[self.current_layer]
        for y in range(self.height):
            for x in range(self.width):
                cell = Gtk.ToggleButton(label="●")
                cell.set_active(layer[y][x])
                cell.set_size_request(68, 68)
                cell.get_style_context().add_class("count-cell")
                cell.set_tooltip_text("Cell %d, %d" % (x + 1, y + 1))
                cell.connect("toggled", self._cell_toggled, x, y)
                self.grid.attach(cell, x, y, 1, 1)

        filled = self._layer_count(layer)
        total = sum(self._layer_count(item) for item in self.layers)
        self.total.set_text(str(total))
        self.summary.set_text("Layer %d of %d   •   %d filled here" %
                              (self.current_layer + 1, len(self.layers), filled))
        for child in self.content.get_children():
            self.content.remove(child)
        if len(self.layers) > 1:
            self.content.pack_start(self.voxels, True, True, 0)
            self.voxels.queue_draw()
        self.content.pack_start(self.grid, False, False, 0)
        self.content.pack_start(self.total_box, False, False, 0)
        self.grid.show_all()
        self.total_box.show_all()
        self.content.show_all()

    def _layer_count(self, layer):
        return sum(sum(row) for row in layer)

    def _cell_toggled(self, button, x, y):
        active = button.get_active()
        if self.layers[self.current_layer][y][x] == active:
            return
        self._record()
        self.layers[self.current_layer][y][x] = active
        self._render()

    def _add_layer(self, *_):
        self._record()
        self.layers.append(self._empty_layer())
        self.current_layer = len(self.layers) - 1
        self._render()

    def _copy_layer(self, *_):
        self._record()
        copied = json.loads(json.dumps(self.layers[self.current_layer]))
        self.layers.insert(self.current_layer + 1, copied)
        self.current_layer += 1
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

    def _draw_voxels(self, widget, cr):
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        ox, oy = width / 2, height / 2 + 80
        sx, sy, depth = 25, 13, 12
        for layer_index in range(len(self.layers) - 1, -1, -1):
            layer = self.layers[layer_index]
            ghost = layer_index != self.current_layer
            alpha = 0.18 if ghost else 0.92
            for y in range(self.height):
                for x in range(self.width):
                    if not layer[y][x]:
                        continue
                    dx = (x - y) * sx
                    dy = (x + y) * sy - layer_index * depth
                    cr.set_source_rgba(0.25, 0.25, 0.25, alpha)
                    cr.move_to(ox + dx, oy + dy - 18)
                    cr.line_to(ox + dx + sx, oy + dy - 18 + sy)
                    cr.line_to(ox + dx, oy + dy - 18 + sy * 2)
                    cr.line_to(ox + dx - sx, oy + dy - 18 + sy)
                    cr.close_path()
                    cr.fill_preserve()
                    cr.set_source_rgba(0.1, 0.1, 0.1, 0.65 if not ghost else 0.25)
                    cr.set_line_width(1.2)
                    cr.stroke()
        cr.set_source_rgba(0.35, 0.35, 0.35, 0.7)
        cr.set_line_width(1)
        for x in range(self.width + 1):
            cr.move_to(ox + (x - self.height) * sx, oy + (x + self.height) * sy)
            cr.line_to(ox + x * sx, oy + x * sy)
        for y in range(self.height + 1):
            cr.move_to(ox + (-y) * sx, oy + y * sy)
            cr.line_to(ox + (self.width - y) * sx, oy + (self.width + y) * sy)
        cr.stroke()

    def _voxel_clicked(self, *_):
        return False

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
