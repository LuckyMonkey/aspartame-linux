"""Native GTK4 Portfolio writing Activity."""

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class PortfolioActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("Portfolio"); self._build()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        root.set_margin_top(28); root.set_margin_bottom(28); root.set_margin_start(32); root.set_margin_end(32)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Portfolio editor"])
        title = Gtk.Label(label="Portfolio", xalign=0); title.add_css_class("title-1"); root.append(title)
        self.name = Gtk.Entry(); self.name.set_placeholder_text("Project title"); self.name.update_property([Gtk.AccessibleProperty.LABEL], ["Project title"]); root.append(self.name)
        self.body = Gtk.TextView(); self.body.set_wrap_mode(Gtk.WrapMode.WORD_CHAR); self.body.update_property([Gtk.AccessibleProperty.LABEL], ["Project description"]); root.append(self.body)
        self.status = Gtk.Label(label="Write about your project.", xalign=0); self.status.add_css_class("dim-label"); root.append(self.status)
        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        save = Gtk.Button(label="Save draft"); save.connect("clicked", self._save); controls.append(save)
        clear = Gtk.Button(label="Clear"); clear.connect("clicked", self._clear); controls.append(clear); root.append(controls)
        self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"entry { min-height: 42px; } textview { min-height: 220px; } button { min-height: 42px; border-radius: 19px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _save(self, _button):
        title = self.name.get_text().strip() or "Untitled project"; self.status.set_text("Draft saved: %s" % title)

    def _clear(self, _button):
        self.name.set_text(""); self.body.get_buffer().set_text(""); self.status.set_text("Write about your project.")
