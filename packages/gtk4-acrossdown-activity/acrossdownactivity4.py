"""Native GTK4 crossword-style Across and Down Activity."""

import json
from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class AcrossDownActivity(SimpleActivity):
    WORDS = (("SUGAR", "A learning desktop"), ("JOURNAL", "Where Sugar saves work"), ("FRAME", "Sugar's navigation border"))

    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Across and Down")
        self.index = 0
        self.buttons = []
        self._build()
        self._render()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        root.set_margin_top(28); root.set_margin_bottom(28); root.set_margin_start(32); root.set_margin_end(32)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Across and Down"])
        title = Gtk.Label(label="Across and Down", xalign=0); title.add_css_class("title-1"); root.append(title)
        self.clue = Gtk.Label(xalign=0); root.append(self.clue)
        self.grid = Gtk.Grid(row_spacing=3, column_spacing=3); self.grid.set_halign(Gtk.Align.CENTER); root.append(self.grid)
        self.entry = Gtk.Entry(); self.entry.set_max_length(1); self.entry.set_placeholder_text("Letter"); self.entry.update_property([Gtk.AccessibleProperty.LABEL], ["Selected letter"]); self.entry.connect("activate", self._set_letter); root.append(self.entry)
        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        set_button = Gtk.Button(label="Set letter"); set_button.connect("clicked", self._set_letter); controls.append(set_button)
        check = Gtk.Button(label="Check word"); check.connect("clicked", self._check); controls.append(check)
        next_button = Gtk.Button(label="Next clue"); next_button.connect("clicked", self._next); controls.append(next_button); root.append(controls)
        self.status = Gtk.Label(xalign=0); self.status.add_css_class("dim-label"); root.append(self.status)
        self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"button { min-width: 90px; min-height: 38px; border-radius: 18px; } entry { min-height: 38px; font-size: 20px; } .cell { min-width: 54px; min-height: 54px; font-size: 22px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _render(self):
        word, clue = self.WORDS[self.index]
        self.clue.set_text("Clue: %s  (%d letters)" % (clue, len(word)))
        self.buttons.clear()
        child = self.grid.get_first_child()
        while child is not None:
            next_child = child.get_next_sibling()
            self.grid.remove(child)
            child = next_child
        for col in range(len(word)):
            button = Gtk.Button(label="_"); button.add_css_class("cell"); button.update_property([Gtk.AccessibleProperty.LABEL], ["Letter %d" % (col + 1)]); button.connect("clicked", self._select, col); self.grid.attach(button, col, 0, 1, 1); self.buttons.append(button)
        self.selected = 0; self.buttons[0].add_css_class("suggested-action")
        self.status.set_text("Select a square, type a letter, then check the word.")

    def _select(self, _button, col):
        self.selected = col
        for button in self.buttons: button.remove_css_class("suggested-action")
        self.buttons[col].add_css_class("suggested-action"); self.entry.grab_focus()

    def _set_letter(self, *_args):
        value = self.entry.get_text().strip().upper()
        if len(value) != 1 or not value.isalpha(): self.status.set_text("Enter one letter."); return
        self.buttons[self.selected].set_label(value); self.selected = (self.selected + 1) % len(self.buttons); self.entry.set_text(""); self._select(self.buttons[self.selected], self.selected)

    def _check(self, _button):
        word, _clue = self.WORDS[self.index]; answer = "".join(button.get_label() for button in self.buttons)
        self.status.set_text("Correct! Choose Next clue." if answer == word else "Not yet — fill every square and try again.")

    def _next(self, _button):
        self.index = (self.index + 1) % len(self.WORDS); self._render()

    def read_file(self, file_path):
        try:
            payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                self.index = int(payload.get("index", 0)) % len(self.WORDS)
                self._render()
                letters = payload.get("letters", [])
                for button, value in zip(self.buttons, letters):
                    button.set_label(str(value)[:1].upper() if str(value)[:1].isalpha() else "_")
                self.selected = min(max(0, int(payload.get("selected", 0))), len(self.buttons) - 1)
                self._select(self.buttons[self.selected], self.selected)
        except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
            return

    def write_file(self, file_path):
        Path(file_path).write_text(json.dumps({"index": self.index, "selected": self.selected, "letters": [button.get_label() for button in self.buttons]}, sort_keys=True) + "\n", encoding="utf-8")
