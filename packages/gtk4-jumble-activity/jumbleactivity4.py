"""GTK4-native word scramble Activity."""

import json
from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class JumbleActivity(SimpleActivity):
    WORDS = (("SUGAR", "A friendly learning desktop"), ("ACTIVITY", "A focused learning tool"), ("JOURNAL", "Where work is saved"))

    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("Jumble"); self.index = 0; self.attempts = 0
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        root.set_margin_top(30); root.set_margin_bottom(30); root.set_margin_start(34); root.set_margin_end(34)
        root.set_hexpand(True); root.set_vexpand(True)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Jumble"]); root.set_accessible_role(Gtk.AccessibleRole.GROUP)
        title = Gtk.Label(label="Jumble", xalign=0); title.add_css_class("title-1"); root.append(title)
        subtitle = Gtk.Label(label="Unscramble each word, then check your answer.", xalign=0); subtitle.add_css_class("dim-label"); subtitle.set_wrap(True); root.append(subtitle)
        panel = Gtk.Frame(label="Word puzzle"); panel.set_halign(Gtk.Align.CENTER); panel.set_valign(Gtk.Align.CENTER); panel.set_hexpand(False); panel.set_vexpand(False); panel.set_size_request(620, -1)
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_margin_top(28); content.set_margin_bottom(28); content.set_margin_start(28); content.set_margin_end(28)
        content.set_valign(Gtk.Align.CENTER)
        self.prompt = Gtk.Label(xalign=0); self.prompt.set_wrap(True); self.prompt.add_css_class("title-2"); self.prompt.update_property([Gtk.AccessibleProperty.LABEL], ["Jumble clue"]); content.append(self.prompt)
        self.entry = Gtk.Entry(); self.entry.set_placeholder_text("Type the unscrambled word"); self.entry.set_hexpand(True); self.entry.update_property([Gtk.AccessibleProperty.LABEL, Gtk.AccessibleProperty.DESCRIPTION], ["Your answer", "Type the unscrambled word"]); self.entry.connect("activate", self._check); content.append(self.entry)
        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        controls.set_halign(Gtk.Align.CENTER)
        check = Gtk.Button(label="Check"); check.update_property([Gtk.AccessibleProperty.LABEL], ["Check answer"]); check.connect("clicked", self._check); controls.append(check)
        next_button = Gtk.Button(label="Next word"); next_button.update_property([Gtk.AccessibleProperty.LABEL], ["Next word"]); next_button.connect("clicked", self._next); controls.append(next_button); content.append(controls)
        self.status = Gtk.Label(xalign=0); self.status.set_opacity(.8); self.status.update_property([Gtk.AccessibleProperty.LABEL], ["Jumble status"]); content.append(self.status)
        panel.set_child(content)
        center = Gtk.CenterBox(); center.set_hexpand(True); center.set_vexpand(True); center.set_center_widget(panel); root.append(center)
        self.set_canvas(root); self._install_css(); self._render()

    def _install_css(self):
        provider = Gtk.CssProvider(); provider.load_from_data(b"frame { border: 2px solid #8aa8b8; border-radius: 8px; padding: 8px; } entry { min-height: 42px; font-size: 20px; } button { min-height: 38px; border-radius: 18px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _render(self):
        word, hint = self.WORDS[self.index]; self.prompt.set_text("Unscramble: %s  ·  Hint: %s" % (" ".join(reversed(word)), hint)); self.status.set_text("Word %d of %d" % (self.index + 1, len(self.WORDS)))

    def _check(self, *_args):
        answer = self.entry.get_text().strip().upper(); word, _hint = self.WORDS[self.index]; self.attempts += 1
        self.status.set_text("Correct! Choose Next word." if answer == word else "Not yet — try again.")

    def _next(self, _button):
        self.index = (self.index + 1) % len(self.WORDS); self.entry.set_text(""); self.attempts = 0; self._render()

    def read_file(self, file_path):
        try:
            payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                self.index = int(payload.get("index", 0)) % len(self.WORDS)
                self.attempts = max(0, int(payload.get("attempts", 0)))
                self.entry.set_text(str(payload.get("answer", "")))
                self._render()
        except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
            return

    def write_file(self, file_path):
        Path(file_path).write_text(json.dumps({"index": self.index, "attempts": self.attempts, "answer": self.entry.get_text()}, sort_keys=True) + "\n", encoding="utf-8")
