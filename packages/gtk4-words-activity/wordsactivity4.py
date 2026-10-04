"""Native GTK4 Words language Activity."""

import json
from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class WordsActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Words")
        self._build()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        root.set_margin_top(28); root.set_margin_bottom(28)
        root.set_margin_start(32); root.set_margin_end(32)
        root.set_hexpand(True); root.set_vexpand(True)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Words translator"])
        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        body.set_hexpand(True); body.set_vexpand(True)
        body.set_halign(Gtk.Align.FILL); body.set_valign(Gtk.Align.FILL)
        root.append(body)
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        card.set_margin_top(22); card.set_margin_bottom(22); card.set_margin_start(22); card.set_margin_end(22)
        card.set_hexpand(True); card.set_vexpand(True)
        card.set_halign(Gtk.Align.FILL); card.set_valign(Gtk.Align.FILL)
        heading = Gtk.Label(label="Words", xalign=0); heading.add_css_class("title-1"); card.append(heading)
        intro = Gtk.Label(label="Type a word to explore it.", xalign=0); intro.add_css_class("dim-label"); card.append(intro)
        self.word = Gtk.Entry(); self.word.set_placeholder_text("Word or phrase")
        self.word.update_property([Gtk.AccessibleProperty.LABEL], ["Word to explore"]); self.word.connect("activate", self._lookup); card.append(self.word)
        lookup = Gtk.Button(label="Explore"); lookup.connect("clicked", self._lookup); card.append(lookup)
        result_frame = Gtk.Frame(label="Meaning and translation")
        result_frame.set_hexpand(True); result_frame.set_vexpand(True)
        self.result = Gtk.Label(label="", xalign=0, yalign=0, wrap=True)
        self.result.set_margin_top(16); self.result.set_margin_bottom(16)
        self.result.set_margin_start(16); self.result.set_margin_end(16)
        self.result.set_hexpand(True); self.result.set_vexpand(True)
        self.result.update_property([Gtk.AccessibleProperty.LABEL], ["Word result"])
        result_frame.set_child(self.result); card.append(result_frame)
        card_frame = Gtk.Frame(label="Word explorer")
        card_frame.set_hexpand(True); card_frame.set_vexpand(True)
        card_frame.set_halign(Gtk.Align.FILL); card_frame.set_valign(Gtk.Align.FILL)
        card_frame.set_child(card); body.append(card_frame)
        self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"frame { border: 1px solid #8aa8b8; border-radius: 10px; } entry { min-height: 44px; } button { min-height: 42px; border-radius: 19px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _lookup(self, _widget):
        value = self.word.get_text().strip()
        self.result.set_text(("Word: " + value + "\nExplore its meaning, spelling, and translation.") if value else "Type a word first.")

    def read_file(self, file_path):
        """Restore the current word from a Journal object."""
        try:
            payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
            value = str(payload.get("word", "")) if isinstance(payload, dict) else ""
        except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
            value = ""
        self.word.set_text(value)
        self._lookup(self.word)

    def write_file(self, file_path):
        """Save the current word as a Journal object."""
        Path(file_path).write_text(json.dumps({"word": self.word.get_text()}, sort_keys=True) + "\n", encoding="utf-8")
