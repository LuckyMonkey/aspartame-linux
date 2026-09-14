"""Native GTK4 Words language Activity."""

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
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Words translator"])
        heading = Gtk.Label(label="Words", xalign=0); heading.add_css_class("title-1"); root.append(heading)
        intro = Gtk.Label(label="Type a word to explore it.", xalign=0); intro.add_css_class("dim-label"); root.append(intro)
        self.word = Gtk.Entry(); self.word.set_placeholder_text("Word or phrase")
        self.word.update_property([Gtk.AccessibleProperty.LABEL], ["Word to explore"]); self.word.connect("activate", self._lookup); root.append(self.word)
        lookup = Gtk.Button(label="Explore"); lookup.connect("clicked", self._lookup); root.append(lookup)
        self.result = Gtk.Label(label="", xalign=0, wrap=True); self.result.update_property([Gtk.AccessibleProperty.LABEL], ["Word result"]); root.append(self.result)
        self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"entry { min-height: 44px; } button { min-height: 42px; border-radius: 19px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _lookup(self, _widget):
        value = self.word.get_text().strip()
        self.result.set_text(("Word: " + value + "\nExplore its meaning, spelling, and translation.") if value else "Type a word first.")
