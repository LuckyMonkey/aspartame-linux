"""Native GTK4 Markdown writing Activity."""

from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class MarkdownActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Markdown")
        self._build()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        root.set_margin_top(24); root.set_margin_bottom(24)
        root.set_margin_start(30); root.set_margin_end(30)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Markdown editor"])
        heading = Gtk.Label(label="Markdown", xalign=0)
        heading.add_css_class("title-1"); root.append(heading)
        self.editor = Gtk.TextView(); self.editor.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.editor.update_property([Gtk.AccessibleProperty.LABEL], ["Markdown source"])
        self.editor.get_buffer().connect("changed", self._render_preview)
        root.append(self.editor)
        preview_title = Gtk.Label(label="Preview", xalign=0)
        preview_title.add_css_class("heading"); root.append(preview_title)
        self.preview = Gtk.Label(label="Start writing with Markdown.", xalign=0, wrap=True)
        self.preview.update_property([Gtk.AccessibleProperty.LABEL], ["Markdown preview"])
        root.append(self.preview)
        clear = Gtk.Button(label="Clear")
        clear.connect("clicked", self._clear); root.append(clear)
        self.set_canvas(root)
        provider = Gtk.CssProvider()
        provider.load_from_data(b"textview { min-height: 280px; } button { min-height: 42px; border-radius: 19px; }")
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _render_preview(self, buffer):
        start, end = buffer.get_bounds()
        text = buffer.get_text(start, end, False).strip()
        self.preview.set_text(text or "Start writing with Markdown.")

    def _clear(self, _button):
        self.editor.get_buffer().set_text("")

    def read_file(self, file_path):
        """Restore UTF-8 Markdown source from a Journal object."""
        try:
            text = Path(file_path).read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            text = ""
        self.editor.get_buffer().set_text(text)

    def write_file(self, file_path):
        """Save UTF-8 Markdown source as the Journal object payload."""
        buffer = self.editor.get_buffer()
        start, end = buffer.get_bounds()
        Path(file_path).write_text(buffer.get_text(start, end, False), encoding="utf-8")
