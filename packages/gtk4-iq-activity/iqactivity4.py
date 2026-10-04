"""Native GTK4 visual sequence puzzle Activity."""

import json
from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class IQActivity(SimpleActivity):
    ROUNDS = (("2, 4, 6, ?", ("7", "8", "9"), "8"), ("3, 6, 12, ?", ("15", "18", "24"), "24"), ("1, 3, 6, ?", ("8", "9", "10"), "10"))

    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("IQ"); self.round = 0; self._build(); self._render()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        root.set_margin_top(32); root.set_margin_bottom(32); root.set_margin_start(36); root.set_margin_end(36)
        root.set_hexpand(True); root.set_vexpand(True)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["IQ puzzle"])
        title = Gtk.Label(label="IQ", xalign=0); title.add_css_class("title-1"); root.append(title)
        panel = Gtk.Frame(label="Sequence puzzle")
        panel.set_hexpand(True); panel.set_vexpand(True)
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        content.set_margin_top(28); content.set_margin_bottom(28); content.set_margin_start(28); content.set_margin_end(28)
        content.set_hexpand(True); content.set_vexpand(True); content.set_valign(Gtk.Align.CENTER)
        self.question = Gtk.Label(xalign=0); self.question.add_css_class("title-2"); content.append(self.question)
        self.options = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.options.set_halign(Gtk.Align.CENTER); content.append(self.options)
        self.status = Gtk.Label(xalign=0); self.status.add_css_class("dim-label"); content.append(self.status)
        next_button = Gtk.Button(label="Next puzzle"); next_button.set_halign(Gtk.Align.CENTER); next_button.connect("clicked", self._next); content.append(next_button)
        panel.set_child(content); root.append(panel)
        self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"frame { border: 2px solid #8aa8b8; border-radius: 8px; padding: 8px; } button { min-width: 100px; min-height: 42px; border-radius: 20px; font-size: 18px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _render(self):
        prompt, choices, _answer = self.ROUNDS[self.round]; self.question.set_text("What comes next?  %s" % prompt)
        child = self.options.get_first_child()
        while child is not None:
            nxt = child.get_next_sibling(); self.options.remove(child); child = nxt
        for choice in choices:
            button = Gtk.Button(label=choice); button.update_property([Gtk.AccessibleProperty.LABEL], ["Answer %s" % choice]); button.connect("clicked", self._answer, choice); self.options.append(button)
        self.status.set_text("Puzzle %d of %d" % (self.round + 1, len(self.ROUNDS)))

    def _answer(self, _button, choice):
        answer = self.ROUNDS[self.round][2]
        self.status.set_text("Correct! Choose Next puzzle." if choice == answer else "Not quite — try another answer.")

    def _next(self, _button):
        self.round = (self.round + 1) % len(self.ROUNDS); self._render()

    def read_file(self, file_path):
        try:
            payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                self.round = int(payload.get("round", 0)) % len(self.ROUNDS)
                self._render()
        except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
            return

    def write_file(self, file_path):
        Path(file_path).write_text(json.dumps({"round": self.round}, sort_keys=True) + "\n", encoding="utf-8")
