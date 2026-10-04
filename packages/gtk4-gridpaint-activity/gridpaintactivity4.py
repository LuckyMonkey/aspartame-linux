"""Native GTK4 Grid Paint Activity."""

import json
from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class GridPaintActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("Grid Paint"); self._build()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        root.set_margin_top(24); root.set_margin_bottom(24); root.set_margin_start(30); root.set_margin_end(30)
        root.set_hexpand(True); root.set_vexpand(True)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Grid Paint canvas"])
        title = Gtk.Label(label="Grid Paint", xalign=0); title.add_css_class("title-1"); root.append(title)
        self.grid = Gtk.Grid(row_spacing=2, column_spacing=2); self.grid.set_hexpand(True); self.grid.set_vexpand(True); self.grid.set_halign(Gtk.Align.FILL); self.grid.set_valign(Gtk.Align.FILL); self.grid.set_column_homogeneous(True); self.grid.set_row_homogeneous(True)
        self.cells = []
        for row in range(10):
            for column in range(10):
                cell = Gtk.ToggleButton(); cell.set_hexpand(True); cell.set_vexpand(True); cell.update_property([Gtk.AccessibleProperty.LABEL], [f"Row {row + 1}, column {column + 1}"]); cell.connect("toggled", self._update_summary); self.grid.attach(cell, column, row, 1, 1)
                self.cells.append(cell)
        board_aspect = Gtk.AspectFrame.new(0.5, 0.5, 1.0, False); board_aspect.set_hexpand(True); board_aspect.set_vexpand(True); board_aspect.set_child(self.grid); root.append(board_aspect)
        self.summary = Gtk.Label(label="0 cells selected", xalign=0); self.summary.update_property([Gtk.AccessibleProperty.LABEL], ["Selection summary"]); root.append(self.summary)
        clear = Gtk.Button(label="Clear picture"); clear.connect("clicked", self._clear); root.append(clear)
        self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"togglebutton:checked { background: #1b6ea8; } button { min-height: 42px; border-radius: 19px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _clear(self, _button):
        for cell in self.cells:
            cell.set_active(False)
        self._update_summary()

    def _update_summary(self, *_args):
        self.summary.set_text(f"{sum(cell.get_active() for cell in self.cells)} cells selected")

    def read_file(self, file_path):
        """Restore selected cells from a JSON Journal object."""
        try:
            payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
            selected = payload.get("selected", []) if isinstance(payload, dict) else []
            if not isinstance(selected, list):
                raise ValueError("selected must be a list")
        except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
            selected = []
        selected = {int(index) for index in selected if isinstance(index, int) and 0 <= index < len(self.cells)}
        for index, cell in enumerate(self.cells):
            cell.set_active(index in selected)
        self._update_summary()

    def write_file(self, file_path):
        """Save selected cells as a JSON Journal object."""
        selected = [index for index, cell in enumerate(self.cells) if cell.get_active()]
        Path(file_path).write_text(json.dumps({"selected": selected}, sort_keys=True) + "\n", encoding="utf-8")
