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
    """A simple physical-feeling counter made from layers of squares."""

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
        self.root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.root.set_name("count-root")
        self.root.set_border_width(16)

        title = Gtk.Label(label="Count")
        title.set_name("count-title")
        self.root.pack_start(title, False, False, 0)

        self.total = Gtk.Label()
        self.total.set_name("count-total")
        self.root.pack_start(self.total, False, False, 0)
        total_label = Gtk.Label(label="total")
        total_label.set_name("count-hint")
        self.root.pack_start(total_label, False, False, 0)

        self.stack_area = Gtk.Overlay()
        self.stack_area.set_size_request(760, 560)
        self.stack_area.set_halign(Gtk.Align.CENTER)
        self.stack_area.set_valign(Gtk.Align.CENTER)
        self.stack_view = Gtk.DrawingArea()
        self.stack_view.connect("draw", self._draw_stack)
        self.stack_area.add(self.stack_view)

        self.grid = Gtk.Grid(row_spacing=4, column_spacing=4)
        self.grid.set_halign(Gtk.Align.CENTER)
        self.grid.set_valign(Gtk.Align.CENTER)
        self.stack_area.add_overlay(self.grid)
        self.root.pack_start(self.stack_area, True, True, 0)

        self.layer_count = Gtk.Label()
        self.layer_count.set_name("count-layer-count")
        self.root.pack_start(self.layer_count, False, False, 0)
        self.layer_total = Gtk.Label()
        self.layer_total.set_name("count-hint")
        self.root.pack_start(self.layer_total, False, False, 0)

        controls = Gtk.Box(spacing=8)
        controls.set_halign(Gtk.Align.CENTER)
        self._symbol_button(controls, "◀", "Previous layer", self._previous_layer)
        self.layer_position = Gtk.Label()
        self.layer_position.set_name("count-layer-position")
        controls.pack_start(self.layer_position, False, False, 4)
        self._symbol_button(controls, "▶", "Next layer", self._next_layer)
        self._symbol_button(controls, "+", "Add layer", self._add_layer)
        self._symbol_button(controls, "⧉", "Copy layer", self._copy_layer)
        self._make_layer_menu(controls)
        self.root.pack_start(controls, False, False, 0)

        self.set_canvas(self.root)
        self._load()
        self._render()
        self.show_all()

    def _install_style(self):
        css = Gtk.CssProvider()
        css.load_from_data(b"""
            #count-root { background: #eeeeee; color: #222222; }
            #count-title { font-size: 26px; font-weight: bold; }
            #count-total { font-size: 48px; font-weight: bold; }
            #count-hint { font-size: 16px; color: #555555; }
            #count-layer-count { font-size: 20px; font-weight: bold; }
            #count-layer-position { font-size: 18px; font-weight: bold; }
            .count-cell { min-width: 68px; min-height: 68px; background: #ffffff;
                          border: 2px solid #777777; border-radius: 5px; }
            .count-cell:checked { background: #444444; }
            .count-symbol { min-width: 38px; min-height: 38px; border-radius: 20px;
                            font-size: 20px; }
        """)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _empty_layer(self):
        return [[False for _ in range(self.width)] for _ in range(self.height)]

    def _symbol_button(self, box, label, help_text, callback):
        button = Gtk.Button(label=label)
        button.set_tooltip_text(help_text)
        button.get_style_context().add_class("count-symbol")
        button.connect("clicked", callback)
        box.pack_start(button, False, False, 0)
        return button

    def _make_layer_menu(self, box):
        menu = Gtk.Menu()
        delete = Gtk.MenuItem(label="Delete layer")
        delete.set_tooltip_text("Remove the layer you are looking at")
        delete.connect("activate", self._delete_layer)
        menu.append(delete)
        menu.show_all()
        more = Gtk.MenuButton()
        more.set_label("⋯")
        more.set_tooltip_text("More layer actions")
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
        for child in self.grid.get_children():
            self.grid.remove(child)
        layer = self.layers[self.current_layer]
        for y in range(self.height):
            for x in range(self.width):
                cell = Gtk.ToggleButton()
                cell.set_active(layer[y][x])
                cell.set_size_request(68, 68)
                cell.get_style_context().add_class("count-cell")
                cell.set_tooltip_text("Thing %d, %d" % (x + 1, y + 1))
                cell.connect("toggled", self._cell_toggled, x, y)
                self.grid.attach(cell, x, y, 1, 1)

        total = sum(self._layer_count(item) for item in self.layers)
        current = self._layer_count(layer)
        self.total.set_text(str(total))
        self.layer_count.set_text("Layer %d of %d" %
                                  (self.current_layer + 1, len(self.layers)))
        self.layer_total.set_text("%d on this layer" % current)
        self.layer_position.set_text("%d / %d" %
                                     (self.current_layer + 1, len(self.layers)))
        self.grid.show_all()
        self.stack_view.queue_draw()

    def _draw_stack(self, widget, cr):
        if len(self.layers) <= 1:
            return
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        grid_width = self.width * 72 - 4
        grid_height = self.height * 72 - 4
        front_x = (width - grid_width) / 2
        front_y = (height - grid_height) / 2
        # Older layers recede up and to the right; they never become floors.
        for index, layer in enumerate(self.layers):
            if index == self.current_layer:
                continue
            distance = abs(index - self.current_layer)
            offset_x = distance * 28
            offset_y = -distance * 18
            alpha = max(0.10, 0.28 - distance * 0.025)
            for y, row in enumerate(layer):
                for x, occupied in enumerate(row):
                    if not occupied:
                        continue
                    left = front_x + offset_x + x * 72
                    top = front_y + offset_y + y * 72
                    cr.set_source_rgba(0.25, 0.25, 0.25, alpha)
                    cr.rectangle(left, top, 68, 68)
                    cr.fill_preserve()
                    cr.set_source_rgba(0.15, 0.15, 0.15, alpha + 0.12)
                    cr.set_line_width(2)
                    cr.stroke()

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
        # New activities start with one empty layer. Journal resume calls read_file.
        return
