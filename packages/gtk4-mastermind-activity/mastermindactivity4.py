"""Small native GTK4 Mastermind Activity.

The game keeps its model independent of the widget tree: six guesses are
scored against a deterministic four-colour secret, making the Activity useful
without a network or legacy GTK runtime.
"""

import json
import random
from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class MastermindActivity(SimpleActivity):
    COLORS = ("red", "blue", "yellow", "green")
    LABELS = {"red": "Red", "blue": "Blue", "yellow": "Yellow", "green": "Green"}

    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Mastermind")
        self.secret = ("red", "blue", "yellow", "green")
        self.guesses = []
        self.current = []

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        root.set_margin_top(24); root.set_margin_bottom(24)
        root.set_margin_start(28); root.set_margin_end(28)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Mastermind"])
        root.set_accessible_role(Gtk.AccessibleRole.GROUP)
        title = Gtk.Label(label="Mastermind", xalign=0)
        title.add_css_class("title-1"); root.append(title)
        self.status = Gtk.Label(label="Choose four colours, then check your code.", xalign=0)
        root.append(self.status)
        self.board = Gtk.Grid(column_spacing=8, row_spacing=8)
        self.board.set_halign(Gtk.Align.CENTER); self.board.set_valign(Gtk.Align.CENTER)
        root.append(self.board)
        self._board_labels = []
        for row in range(6):
            cells = []
            for col in range(4):
                cell = Gtk.Label(label="·")
                cell.set_size_request(64, 42); cell.add_css_class("peg")
                self.board.attach(cell, col, row, 1, 1); cells.append(cell)
            self._board_labels.append(cells)
        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self._choices = []
        for color in self.COLORS:
            button = Gtk.Button(label=self.LABELS[color])
            button.add_css_class(color); button.connect("clicked", self._choose, color)
            button.update_property([Gtk.AccessibleProperty.LABEL], [self.LABELS[color]])
            controls.append(button); self._choices.append(button)
        check = Gtk.Button(label="Check code"); check.connect("clicked", self._check)
        controls.append(check)
        reset = Gtk.Button(label="New game"); reset.connect("clicked", self._reset)
        controls.append(reset)
        root.append(controls)
        self.set_canvas(root)
        self._install_css(); self._render()

    def _install_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(b"""
            .peg { background: #e8edf0; border: 1px solid #637985; border-radius: 22px; padding: 8px; font-size: 22px; }
            button { min-height: 38px; border-radius: 18px; }
            button.red { background: #d95b5b; color: white; } button.blue { background: #4b9de8; color: white; }
            button.yellow { background: #e8c44b; color: #222; } button.green { background: #56b878; color: white; }
        """)
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _choose(self, _button, color):
        if len(self.current) < 4 and len(self.guesses) < 6:
            self.current.append(color); self._render()

    def _check(self, _button):
        if len(self.current) != 4:
            self.status.set_text("Choose four colours before checking."); return
        if len(self.guesses) >= 6: return
        guess = tuple(self.current); self.guesses.append(guess); self.current = []
        exact = sum(a == b for a, b in zip(guess, self.secret))
        common = sum(min(guess.count(c), self.secret.count(c)) for c in self.COLORS)
        if exact == 4:
            self.status.set_text("Code cracked! Start a new game to play again.")
        elif len(self.guesses) == 6:
            self.status.set_text("No guesses left. Start a new game to try again.")
        else:
            self.status.set_text("%d exact, %d colour match%s. Keep trying." % (exact, common - exact, "" if common - exact == 1 else "es"))
        self._render()

    def _reset(self, _button):
        self.secret = tuple(random.Random(42 + len(self.guesses)).choice(self.COLORS) for _ in range(4))
        self.guesses = []; self.current = []; self.status.set_text("Choose four colours, then check your code."); self._render()

    def _render(self):
        for row, cells in enumerate(self._board_labels):
            values = self.guesses[row] if row < len(self.guesses) else (self.current if row == len(self.guesses) else ())
            for col, cell in enumerate(cells):
                value = values[col] if col < len(values) else "·"
                cell.set_text("●" if value != "·" else "·")
                for color in self.COLORS: cell.remove_css_class(color)
                if value != "·": cell.add_css_class(value)
                cell.update_property([Gtk.AccessibleProperty.LABEL], [self.LABELS.get(value, "Empty") + " peg"])

    def read_file(self, file_path):
        """Restore the deterministic code and guesses from Journal."""
        try:
            payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
            secret = tuple(payload.get("secret", self.secret))
            guesses = payload.get("guesses", [])
            current = payload.get("current", [])
            valid = lambda seq: isinstance(seq, (list, tuple)) and all(value in self.COLORS for value in seq)
            if len(secret) != 4 or not valid(secret) or not isinstance(guesses, list) or any(len(row) != 4 or not valid(row) for row in guesses) or not valid(current) or len(current) > 4:
                raise ValueError("invalid Mastermind state")
            self.secret = secret; self.guesses = [tuple(row) for row in guesses]; self.current = list(current)
            self.status.set_text("Code cracked! Start a new game to play again." if self.guesses and self.guesses[-1] == self.secret else "Choose four colours, then check your code.")
            self._render()
        except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
            self.secret = ("red", "blue", "yellow", "green"); self.guesses = []; self.current = []; self._render()

    def write_file(self, file_path):
        """Persist Mastermind progress as a Journal object."""
        Path(file_path).write_text(json.dumps({"secret": self.secret, "guesses": self.guesses, "current": self.current}, sort_keys=True) + "\n", encoding="utf-8")
