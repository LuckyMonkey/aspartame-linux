"""Native GTK4 Go board Activity."""

import json
from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class PlayGoActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("PlayGo"); self.turn = 1; self.board = [0] * 25; self._build(); self._render()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        root.set_margin_top(28); root.set_margin_bottom(28); root.set_margin_start(32); root.set_margin_end(32)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["PlayGo board"])
        title = Gtk.Label(label="PlayGo", xalign=0); title.add_css_class("title-1"); root.append(title)
        root.append(Gtk.Label(label="Place black and white stones on the board.", xalign=0))
        self.grid = Gtk.Grid(row_spacing=2, column_spacing=2); self.grid.set_halign(Gtk.Align.CENTER); root.append(self.grid)
        self.status = Gtk.Label(xalign=0); self.status.add_css_class("dim-label"); root.append(self.status)
        reset = Gtk.Button(label="New game"); reset.connect("clicked", self._reset); root.append(reset)
        self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"button { min-width: 48px; min-height: 48px; border-radius: 24px; font-size: 18px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _render(self):
        child = self.grid.get_first_child()
        while child is not None:
            nxt = child.get_next_sibling(); self.grid.remove(child); child = nxt
        for index, value in enumerate(self.board):
            label = "" if value == 0 else ("●" if value == 1 else "○")
            button = Gtk.Button(label=label); button.update_property([Gtk.AccessibleProperty.LABEL], ["Intersection %d" % (index + 1)]); button.connect("clicked", self._place, index); self.grid.attach(button, index % 5, index // 5, 1, 1)
        self.status.set_text("Black to play" if self.turn == 1 else "White to play")

    def _place(self, _button, index):
        if self.board[index] != 0: self.status.set_text("That intersection is occupied."); return
        self.board[index] = self.turn; self.turn = 2 if self.turn == 1 else 1; self._render()

    def _reset(self, _button):
        self.board = [0] * 25; self.turn = 1; self._render()

    def read_file(self, file_path):
        try:
            payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
            board = payload.get("board") if isinstance(payload, dict) else None
            if isinstance(board, list) and len(board) == 25:
                self.board = [int(value) if int(value) in (0, 1, 2) else 0 for value in board]
                self.turn = int(payload.get("turn", 1)) if int(payload.get("turn", 1)) in (1, 2) else 1
                self._render()
        except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
            return

    def write_file(self, file_path):
        Path(file_path).write_text(json.dumps({"board": self.board, "turn": self.turn}, sort_keys=True) + "\n", encoding="utf-8")
