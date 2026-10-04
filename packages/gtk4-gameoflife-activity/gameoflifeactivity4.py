"""Native GTK4 Conway's Game of Life Activity."""

import json
from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class GameOfLifeActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("Game Of Life"); self._cells = set(); self.generation = 0; self._build()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10); root.set_margin_top(24); root.set_margin_bottom(24); root.set_margin_start(30); root.set_margin_end(30); root.set_hexpand(True); root.set_vexpand(True); root.update_property([Gtk.AccessibleProperty.LABEL], ["Game of Life grid"])
        title = Gtk.Label(label="Game Of Life", xalign=0); title.add_css_class("title-1"); root.append(title)
        instruction = Gtk.Label(label="Click cells to make a pattern, then use Step to watch it evolve.", xalign=0)
        instruction.add_css_class("dim-label"); instruction.set_wrap(True); root.append(instruction)
        self.grid = Gtk.Grid(row_spacing=2, column_spacing=2); self.grid.set_hexpand(True); self.grid.set_vexpand(True); self.grid.set_halign(Gtk.Align.FILL); self.grid.set_valign(Gtk.Align.FILL); self.grid.set_column_homogeneous(True); self.grid.set_row_homogeneous(True); self.buttons = {}
        for row in range(12):
            for column in range(12):
                button = Gtk.ToggleButton(); button.set_hexpand(True); button.set_vexpand(True); button.update_property([Gtk.AccessibleProperty.LABEL], [f"Row {row + 1}, column {column + 1}"]); button.connect("toggled", self._changed, row, column); self.grid.attach(button, column, row, 1, 1); self.buttons[(row, column)] = button
        board_aspect = Gtk.AspectFrame.new(0.5, 0.5, 1.0, False); board_aspect.set_hexpand(True); board_aspect.set_vexpand(True); board_aspect.set_child(self.grid)
        board_frame = Gtk.Frame(label="Life board"); board_frame.set_hexpand(True); board_frame.set_vexpand(True); board_frame.set_child(board_aspect); root.append(board_frame); self.summary = Gtk.Label(label="Generation: 0 · 0 cells", xalign=0); self.summary.add_css_class("dim-label"); self.summary.update_property([Gtk.AccessibleProperty.LABEL], ["Generation summary"]); root.append(self.summary); controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8); controls.set_halign(Gtk.Align.CENTER)
        step = Gtk.Button(label="Step"); step.update_property([Gtk.AccessibleProperty.LABEL], ["Advance one Game of Life generation"]); step.connect("clicked", self._step); controls.append(step)
        clear = Gtk.Button(label="Clear"); clear.update_property([Gtk.AccessibleProperty.LABEL], ["Clear Game of Life board"]); clear.connect("clicked", self._clear); controls.append(clear); root.append(controls)
        self.set_canvas(root); provider = Gtk.CssProvider(); provider.load_from_data(b"frame { border: 2px solid #8aa8b8; border-radius: 8px; padding: 8px; } togglebutton:checked { background: #2c78a8; } button { min-height: 42px; border-radius: 19px; }"); display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _changed(self, button, row, column):
        (self._cells.add if button.get_active() else self._cells.discard)((row, column))
        self._update_summary()

    def _step(self, _button):
        neighbors = {}
        for row, column in self._cells:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr or dc: neighbors[(row + dr, column + dc)] = neighbors.get((row + dr, column + dc), 0) + 1
        self._cells = {cell for cell, count in neighbors.items() if count == 3 or (count == 2 and cell in self._cells)}; self.generation += 1; self._refresh(); self._update_summary()

    def _refresh(self):
        for cell, button in self.buttons.items(): button.handler_block_by_func(self._changed); button.set_active(cell in self._cells); button.handler_unblock_by_func(self._changed)

    def _clear(self, _button): self._cells.clear(); self.generation = 0; self._refresh(); self._update_summary()

    def _update_summary(self): self.summary.set_text(f"Generation: {self.generation} · {len(self._cells)} cells")

    def read_file(self, file_path):
        """Restore live cells and generation from a JSON Journal object."""
        try:
            payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
            cells = payload.get("cells", []) if isinstance(payload, dict) else []
            generation = payload.get("generation", 0) if isinstance(payload, dict) else 0
            self._cells = {(int(cell[0]), int(cell[1])) for cell in cells if isinstance(cell, list) and len(cell) == 2 and 0 <= int(cell[0]) < 12 and 0 <= int(cell[1]) < 12}
            self.generation = max(0, int(generation))
        except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
            self._cells, self.generation = set(), 0
        self._refresh(); self._update_summary()

    def write_file(self, file_path):
        """Save live cells and generation as a JSON Journal object."""
        Path(file_path).write_text(json.dumps({"cells": sorted(self._cells), "generation": self.generation}, sort_keys=True) + "\n", encoding="utf-8")
