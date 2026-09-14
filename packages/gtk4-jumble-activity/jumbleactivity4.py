"""GTK4-native word scramble Activity."""

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class JumbleActivity(SimpleActivity):
    WORDS = (("SUGAR", "A friendly learning desktop"), ("ACTIVITY", "A focused learning tool"), ("JOURNAL", "Where work is saved"))

    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("Jumble"); self.index = 0; self.attempts = 0
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        root.set_margin_top(30); root.set_margin_bottom(30); root.set_margin_start(34); root.set_margin_end(34)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Jumble"]); root.set_accessible_role(Gtk.AccessibleRole.GROUP)
        title = Gtk.Label(label="Jumble", xalign=0); title.add_css_class("title-1"); root.append(title)
        self.prompt = Gtk.Label(xalign=0); root.append(self.prompt)
        self.entry = Gtk.Entry(); self.entry.set_placeholder_text("Type the unscrambled word"); self.entry.update_property([Gtk.AccessibleProperty.LABEL], ["Your answer"]); self.entry.connect("activate", self._check); root.append(self.entry)
        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        check = Gtk.Button(label="Check"); check.connect("clicked", self._check); controls.append(check)
        next_button = Gtk.Button(label="Next word"); next_button.connect("clicked", self._next); controls.append(next_button); root.append(controls)
        self.status = Gtk.Label(xalign=0); self.status.set_opacity(.8); root.append(self.status)
        self.set_canvas(root); self._install_css(); self._render()

    def _install_css(self):
        provider = Gtk.CssProvider(); provider.load_from_data(b"entry { min-height: 42px; font-size: 20px; } button { min-height: 38px; border-radius: 18px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _render(self):
        word, hint = self.WORDS[self.index]; self.prompt.set_text("Unscramble: %s  ·  Hint: %s" % (" ".join(reversed(word)), hint)); self.status.set_text("Word %d of %d" % (self.index + 1, len(self.WORDS)))

    def _check(self, *_args):
        answer = self.entry.get_text().strip().upper(); word, _hint = self.WORDS[self.index]; self.attempts += 1
        self.status.set_text("Correct! Choose Next word." if answer == word else "Not yet — try again.")

    def _next(self, _button):
        self.index = (self.index + 1) % len(self.WORDS); self.entry.set_text(""); self.attempts = 0; self._render()

