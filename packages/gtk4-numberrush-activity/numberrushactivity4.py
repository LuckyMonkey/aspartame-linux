"""GTK4-native arithmetic practice Activity."""

import json
from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class NumberRushActivity(SimpleActivity):
    ROUNDS = ((7, 5), (12, 8), (9, 6), (15, 4), (11, 9))

    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("Number Rush"); self.round = 0; self.score = 0; self.solved = False
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        root.set_margin_top(30); root.set_margin_bottom(30); root.set_margin_start(34); root.set_margin_end(34)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Number Rush"]); root.set_accessible_role(Gtk.AccessibleRole.GROUP)
        title = Gtk.Label(label="Number Rush", xalign=0); title.add_css_class("title-1"); root.append(title)
        self.prompt = Gtk.Label(xalign=0); root.append(self.prompt)
        self.answer = Gtk.Entry(); self.answer.set_placeholder_text("Type the answer"); self.answer.update_property([Gtk.AccessibleProperty.LABEL], ["Answer"]); self.answer.connect("activate", self._check); root.append(self.answer)
        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        check = Gtk.Button(label="Check"); check.connect("clicked", self._check); controls.append(check)
        next_button = Gtk.Button(label="Next round"); next_button.connect("clicked", self._next); controls.append(next_button); root.append(controls)
        self.status = Gtk.Label(xalign=0); self.status.set_opacity(.8); root.append(self.status)
        self.set_canvas(root); self._install_css(); self._render()

    def _install_css(self):
        provider = Gtk.CssProvider(); provider.load_from_data(b"entry { min-height: 42px; font-size: 20px; } button { min-height: 38px; border-radius: 18px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _render(self):
        left, right = self.ROUNDS[self.round]; self.prompt.set_text("Round %d of %d: %d + %d = ?" % (self.round + 1, len(self.ROUNDS), left, right)); self.status.set_text("Score: %d" % self.score)

    def _check(self, *_args):
        left, right = self.ROUNDS[self.round]
        try: answer = int(self.answer.get_text())
        except ValueError: self.status.set_text("Enter a whole number."); return
        if answer == left + right:
            if not self.solved: self.score += 1; self.solved = True
            self.status.set_text("Correct! Score: %d" % self.score)
        else: self.status.set_text("Try again — the answer is a little different.")

    def _next(self, _button):
        self.round = (self.round + 1) % len(self.ROUNDS); self.answer.set_text(""); self.solved = False; self._render()

    def read_file(self, file_path):
        try:
            payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                self.round = int(payload.get("round", 0)) % len(self.ROUNDS)
                self.score = max(0, int(payload.get("score", 0)))
                self.solved = bool(payload.get("solved", False))
                self.answer.set_text(str(payload.get("answer", "")))
                self._render()
        except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
            return

    def write_file(self, file_path):
        Path(file_path).write_text(json.dumps({"round": self.round, "score": self.score, "solved": self.solved, "answer": self.answer.get_text()}, sort_keys=True) + "\n", encoding="utf-8")
