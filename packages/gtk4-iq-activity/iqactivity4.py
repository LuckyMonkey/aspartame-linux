"""Native GTK4 visual sequence puzzle Activity."""

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class IQActivity(SimpleActivity):
    ROUNDS = (("2, 4, 6, ?", ("7", "8", "9"), "8"), ("3, 6, 12, ?", ("15", "18", "24"), "24"), ("1, 3, 6, ?", ("8", "9", "10"), "10"))

    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("IQ"); self.round = 0; self._build(); self._render()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        root.set_margin_top(32); root.set_margin_bottom(32); root.set_margin_start(36); root.set_margin_end(36)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["IQ puzzle"])
        title = Gtk.Label(label="IQ", xalign=0); title.add_css_class("title-1"); root.append(title)
        self.question = Gtk.Label(xalign=0); root.append(self.question)
        self.options = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10); root.append(self.options)
        self.status = Gtk.Label(xalign=0); self.status.add_css_class("dim-label"); root.append(self.status)
        next_button = Gtk.Button(label="Next puzzle"); next_button.connect("clicked", self._next); root.append(next_button)
        self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"button { min-width: 100px; min-height: 42px; border-radius: 20px; font-size: 18px; }")
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
