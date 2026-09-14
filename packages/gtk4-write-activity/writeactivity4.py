"""Native GTK4 Write document Activity."""

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class WriteActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("Write"); self._build()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10); root.set_margin_top(24); root.set_margin_bottom(24); root.set_margin_start(30); root.set_margin_end(30); root.update_property([Gtk.AccessibleProperty.LABEL], ["Write document"])
        title = Gtk.Label(label="Write", xalign=0); title.add_css_class("title-1"); root.append(title)
        self.document = Gtk.TextView(); self.document.set_wrap_mode(Gtk.WrapMode.WORD_CHAR); self.document.set_vexpand(True); self.document.update_property([Gtk.AccessibleProperty.LABEL], ["Document text"]); root.append(self.document)
        self.status = Gtk.Label(label="Ready", xalign=0); self.status.add_css_class("dim-label"); root.append(self.status)
        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        save = Gtk.Button(label="Save draft"); save.connect("clicked", self._save); controls.append(save)
        clear = Gtk.Button(label="Clear"); clear.connect("clicked", self._clear); controls.append(clear); root.append(controls)
        self.set_canvas(root); provider = Gtk.CssProvider(); provider.load_from_data(b"textview { min-height: 360px; } button { min-height: 42px; border-radius: 19px; }"); display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _save(self, _button):
        start, end = self.document.get_buffer().get_bounds(); count = len(self.document.get_buffer().get_text(start, end, False)); self.status.set_text(f"Draft saved ({count} characters)")

    def _clear(self, _button): self.document.get_buffer().set_text(""); self.status.set_text("Ready")
