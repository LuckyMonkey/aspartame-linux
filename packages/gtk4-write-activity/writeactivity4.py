"""Native GTK4 Write document Activity.

The toolkit owns the Journal object and calls :meth:`read_file` and
:meth:`write_file` around resume/save.  Keeping the document payload as UTF-8
text preserves the normal Sugar Activity file boundary without coupling this
Activity to datastore internals.
"""

from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class WriteActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("Write"); self._build()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10); root.set_margin_top(24); root.set_margin_bottom(24); root.set_margin_start(30); root.set_margin_end(30); root.set_hexpand(True); root.set_vexpand(True); root.update_property([Gtk.AccessibleProperty.LABEL], ["Write document"])
        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10); body.set_hexpand(True); body.set_halign(Gtk.Align.FILL); body.set_valign(Gtk.Align.FILL); body.set_vexpand(True); root.append(body)
        title = Gtk.Label(label="Write", xalign=0); title.add_css_class("title-1"); body.append(title)
        self.document = Gtk.TextView(); self.document.set_wrap_mode(Gtk.WrapMode.WORD_CHAR); self.document.set_hexpand(True); self.document.set_vexpand(True); self.document.update_property([Gtk.AccessibleProperty.LABEL], ["Document text"])
        document_scroll = Gtk.ScrolledWindow(); document_scroll.set_min_content_height(520); document_scroll.set_hexpand(True); document_scroll.set_vexpand(True); document_scroll.set_child(self.document)
        document_frame = Gtk.Frame(label="Document"); document_frame.set_hexpand(True); document_frame.set_vexpand(True); document_frame.set_child(document_scroll); body.append(document_frame)
        self.status = Gtk.Label(label="Ready", xalign=0); self.status.add_css_class("dim-label"); body.append(self.status)
        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        save = Gtk.Button(label="Save draft"); save.connect("clicked", self._save); controls.append(save)
        clear = Gtk.Button(label="Clear"); clear.connect("clicked", self._clear); controls.append(clear); body.append(controls)
        self.set_canvas(root); provider = Gtk.CssProvider(); provider.load_from_data(b"scrolledwindow { border: 1px solid #8aa8b8; border-radius: 8px; } textview { padding: 14px; } button { min-height: 42px; border-radius: 19px; }"); display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _save(self, _button):
        start, end = self.document.get_buffer().get_bounds()
        count = len(self.document.get_buffer().get_text(start, end, False))
        self.save()
        self.status.set_text(f"Draft saved ({count} characters)")

    def _clear(self, _button): self.document.get_buffer().set_text(""); self.status.set_text("Ready")

    def read_file(self, file_path):
        """Restore the document body from a Journal object."""
        try:
            text = Path(file_path).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            self.status.set_text(f"Unable to open draft: {error}")
            return
        self.document.get_buffer().set_text(text)
        self.status.set_text(f"Draft restored ({len(text)} characters)")

    def write_file(self, file_path):
        """Write the current document body for the Journal datastore."""
        start, end = self.document.get_buffer().get_bounds()
        text = self.document.get_buffer().get_text(start, end, False)
        try:
            Path(file_path).write_text(text, encoding="utf-8")
        except OSError as error:
            self.status.set_text(f"Unable to save draft: {error}")
            raise
