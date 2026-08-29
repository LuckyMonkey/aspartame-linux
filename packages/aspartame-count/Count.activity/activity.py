#!/usr/bin/env python3
import json
import os
from gettext import gettext as _

from gi import require_version
require_version("Gdk", "3.0")
require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk
from sugar3.activity import activity
from sugar3.activity.widgets import ActivityToolbarButton, StopButton
from sugar3.graphics.toolbarbox import ToolbarBox


class CountActivity(activity.Activity):
    """A small, persistent Sugar Activity for counting grid cells."""

    def __init__(self, handle):
        super().__init__(handle)
        self.width, self.height = 5, 4
        self.layers = [[[False for _ in range(self.width)]
                        for _ in range(self.height)]]
        self.current_layer = 0
        self.undo_stack, self.redo_stack = [], []
        self.cells = []

        toolbar = ToolbarBox()
        toolbar.toolbar.insert(ActivityToolbarButton(self), -1)
        toolbar.toolbar.insert(Gtk.SeparatorToolItem(), -1)
        self._button(toolbar, _("Previous layer"), self._previous_layer)
        self._button(toolbar, _("Next layer"), self._next_layer)
        self._button(toolbar, _("Add layer"), self._add_layer)
        self._button(toolbar, _("Duplicate"), self._duplicate_layer)
        self._button(toolbar, _("Delete layer"), self._delete_layer)
        self._button(toolbar, _("Clear layer"), self._clear_layer)
        self._button(toolbar, _("Undo"), self._undo)
        self._button(toolbar, _("Redo"), self._redo)
        toolbar.toolbar.insert(StopButton(self), -1)
        toolbar.show_all()
        self.set_toolbar_box(toolbar)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        root.set_border_width(12)
        self.summary = Gtk.Label()
        self.summary.set_xalign(0)
        root.pack_start(self.summary, False, False, 0)
        controls = Gtk.Box(spacing=6)
        self._button(controls, _("X +"), self._grow_x)
        self._button(controls, _("X -"), self._shrink_x)
        self._button(controls, _("Y +"), self._grow_y)
        self._button(controls, _("Y -"), self._shrink_y)
        root.pack_start(controls, False, False, 0)
        self.grid = Gtk.Grid(row_spacing=3, column_spacing=3)
        self.grid.set_halign(Gtk.Align.CENTER)
        self.grid.set_valign(Gtk.Align.CENTER)
        root.pack_start(self.grid, True, True, 0)
        self.set_canvas(root)
        self._load()
        self._render()

    def _button(self, box, label, callback):
        button = Gtk.ToolButton.new(None, label)
        button.connect("clicked", callback)
        if hasattr(box, "toolbar"):
            box.toolbar.insert(button, -1)
        else:
            plain = Gtk.Button(label=label)
            plain.connect("clicked", callback)
            box.pack_start(plain, False, False, 0)
            return plain
        return button

    def _snapshot(self):
        return json.loads(json.dumps({"width": self.width, "height": self.height,
                                      "layers": self.layers, "current_layer": self.current_layer}))

    def _record(self):
        self.undo_stack.append(self._snapshot())
        self.redo_stack.clear()

    def _restore(self, state):
        self.width, self.height = state["width"], state["height"]
        self.layers, self.current_layer = state["layers"], state["current_layer"]
        self.current_layer = min(self.current_layer, len(self.layers) - 1)
        self._render()

    def _render(self):
        for child in self.grid.get_children():
            self.grid.remove(child)
        self.cells = []
        layer = self.layers[self.current_layer]
        for y in range(self.height):
            row = []
            for x in range(self.width):
                button = Gtk.ToggleButton(label="●")
                button.set_active(layer[y][x])
                button.set_size_request(54, 54)
                button.set_tooltip_text(_("Cell %d, %d") % (x + 1, y + 1))
                button.connect("toggled", self._cell_toggled, x, y)
                self.grid.attach(button, x, y, 1, 1)
                row.append(button)
            self.cells.append(row)
        total = sum(sum(row) for current in self.layers for row in current)
        filled = sum(sum(row) for row in layer)
        rectangular = all(all(cell for cell in row) for row in layer)
        expression = "%d × %d = %d" % (self.width, self.height, filled) if rectangular else _("irregular layer")
        self.summary.set_text(_("Count  •  Layer %d/%d  •  %s  •  Total: %d") %
                              (self.current_layer + 1, len(self.layers), expression, total))
        self.grid.show_all()

    def _cell_toggled(self, button, x, y):
        layer = self.layers[self.current_layer]
        if layer[y][x] != button.get_active():
            self._record()
            layer[y][x] = button.get_active()
            self._render()

    def _resize(self, width, height):
        if width < 1 or height < 1 or (width == self.width and height == self.height): return
        self._record()
        for layer in self.layers:
            layer[:] = [row[:width] + [False] * max(0, width - len(row)) for row in layer[:height]]
            layer.extend([[False] * width for _ in range(height - len(layer))])
        self.width, self.height = width, height
        self._render()

    def _grow_x(self, *_): self._resize(self.width + 1, self.height)
    def _shrink_x(self, *_): self._resize(self.width - 1, self.height)
    def _grow_y(self, *_): self._resize(self.width, self.height + 1)
    def _shrink_y(self, *_): self._resize(self.width, self.height - 1)
    def _previous_layer(self, *_): self.current_layer = max(0, self.current_layer - 1); self._render()
    def _next_layer(self, *_): self.current_layer = min(len(self.layers) - 1, self.current_layer + 1); self._render()
    def _add_layer(self, *_): self._record(); self.layers.append([[False] * self.width for _ in range(self.height)]); self.current_layer = len(self.layers) - 1; self._render()
    def _duplicate_layer(self, *_): self._record(); self.layers.insert(self.current_layer + 1, json.loads(json.dumps(self.layers[self.current_layer]))); self.current_layer += 1; self._render()
    def _delete_layer(self, *_):
        if len(self.layers) == 1: return
        self._record(); self.layers.pop(self.current_layer); self.current_layer = min(self.current_layer, len(self.layers) - 1); self._render()
    def _clear_layer(self, *_): self._record(); self.layers[self.current_layer] = [[False] * self.width for _ in range(self.height)]; self._render()
    def _undo(self, *_):
        if self.undo_stack: self.redo_stack.append(self._snapshot()); self._restore(self.undo_stack.pop())
    def _redo(self, *_):
        if self.redo_stack: self.undo_stack.append(self._snapshot()); self._restore(self.redo_stack.pop())

    def write_file(self, file_path):
        with open(file_path, "w", encoding="utf-8") as stream:
            json.dump(self._snapshot(), stream)

    def read_file(self, file_path):
        with open(file_path, encoding="utf-8") as stream:
            state = json.load(stream)
        if state.get("layers"):
            self._restore(state)

    def _load(self):
        pass
