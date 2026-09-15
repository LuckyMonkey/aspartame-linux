"""Native GTK4 Typing Turtle practice Activity."""

import json
from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class TypingTurtleActivity(SimpleActivity):
    WORDS = ("sugar", "activity", "journal", "turtle")

    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("Typing Turtle"); self.index = 0; self._build(); self._render()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        root.set_margin_top(32); root.set_margin_bottom(32); root.set_margin_start(36); root.set_margin_end(36)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Typing Turtle exercise"])
        title = Gtk.Label(label="Typing Turtle", xalign=0); title.add_css_class("title-1"); root.append(title)
        self.prompt = Gtk.Label(xalign=0); root.append(self.prompt)
        self.entry = Gtk.Entry(); self.entry.set_placeholder_text("Type the word"); self.entry.update_property([Gtk.AccessibleProperty.LABEL], ["Typing answer"]); self.entry.connect("activate", self._check); root.append(self.entry)
        self.status = Gtk.Label(xalign=0); self.status.add_css_class("dim-label"); root.append(self.status)
        next_button = Gtk.Button(label="Next word"); next_button.connect("clicked", self._next); root.append(next_button)
        self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"entry { min-height: 44px; font-size: 20px; } button { min-height: 42px; border-radius: 19px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _render(self):
        self.prompt.set_text("Type: %s" % self.WORDS[self.index]); self.status.set_text("Word %d of %d" % (self.index + 1, len(self.WORDS))); self.entry.set_text(""); self.entry.grab_focus()

    def _check(self, *_args):
        expected = self.WORDS[self.index]; typed = self.entry.get_text().strip().casefold(); self.status.set_text("Correct! Choose Next word." if typed == expected else "Keep trying — check the letters.")

    def _next(self, _button):
        self.index = (self.index + 1) % len(self.WORDS); self._render()

    def read_file(self, file_path):
        """Restore the current exercise index from a JSON Journal object."""
        try:
            payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
            index = int(payload.get("index", 0)) if isinstance(payload, dict) else 0
        except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
            index = 0
        self.index = index % len(self.WORDS)
        self._render()

    def write_file(self, file_path):
        """Save the current exercise index as a JSON Journal object."""
        Path(file_path).write_text(json.dumps({"index": self.index}, sort_keys=True) + "\n", encoding="utf-8")
