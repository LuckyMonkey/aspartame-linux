"""Native GTK4 Markdown writing Activity."""

from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity
from markdown_renderer import render_markdown


DEFAULT_MARKDOWN = "# Welcome to Markdown\n\nStart writing here. The preview updates as you type."


class MarkdownActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Markdown")
        self._build()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        root.set_margin_top(24); root.set_margin_bottom(24)
        root.set_margin_start(30); root.set_margin_end(30)
        root.set_hexpand(True); root.set_vexpand(True)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Markdown editor"])
        heading = Gtk.Label(label="Markdown", xalign=0)
        heading.add_css_class("markdown-title"); root.append(heading)
        intro = Gtk.Label(
            label="Write Markdown on the left and review the source preview on the right.",
            xalign=0, wrap=True)
        intro.add_css_class("dim-label"); root.append(intro)
        self.editor = Gtk.TextView()
        self.editor.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.editor.set_hexpand(True); self.editor.set_vexpand(True)
        self.editor.set_monospace(True)
        self.editor.update_property([Gtk.AccessibleProperty.LABEL], ["Markdown source"])
        self.editor.get_buffer().connect("changed", self._render_preview)
        editor_scroll = Gtk.ScrolledWindow()
        editor_scroll.set_min_content_width(340); editor_scroll.set_min_content_height(280)
        editor_scroll.set_hexpand(True); editor_scroll.set_vexpand(True)
        editor_scroll.set_child(self.editor)
        editor_surface = Gtk.Overlay()
        editor_surface.set_hexpand(True); editor_surface.set_vexpand(True)
        editor_surface.set_child(editor_scroll)
        self.editor_empty = Gtk.Label(
            label="Start writing Markdown here.", wrap=True, xalign=0.5)
        self.editor_empty.add_css_class("editor-empty-state")
        self.editor_empty.set_halign(Gtk.Align.CENTER); self.editor_empty.set_valign(Gtk.Align.CENTER)
        self.editor_empty.set_can_target(False); self.editor_empty.set_max_width_chars(36)
        self.editor_empty.update_property([Gtk.AccessibleProperty.LABEL], ["Empty Markdown editor"])
        editor_surface.add_overlay(self.editor_empty)
        editor_frame = Gtk.Frame(label="Markdown source")
        editor_frame.add_css_class("editor-pane")
        editor_frame.set_hexpand(True); editor_frame.set_vexpand(True)
        editor_frame.set_child(editor_surface)
        self.preview = Gtk.Label(label="Start writing with Markdown.", xalign=0, wrap=True)
        self.preview.set_selectable(True)
        self.preview.set_yalign(0.0)
        self.preview.set_margin_top(14); self.preview.set_margin_bottom(14)
        self.preview.set_margin_start(14); self.preview.set_margin_end(14)
        self.preview.update_property([Gtk.AccessibleProperty.LABEL], ["Markdown preview"])
        preview_scroll = Gtk.ScrolledWindow()
        preview_scroll.set_min_content_width(340); preview_scroll.set_min_content_height(160)
        preview_scroll.set_hexpand(True); preview_scroll.set_vexpand(True)
        preview_scroll.set_child(self.preview)
        preview_frame = Gtk.Frame(label="Preview")
        preview_frame.add_css_class("editor-pane")
        preview_frame.set_hexpand(True); preview_frame.set_vexpand(True)
        preview_frame.set_child(preview_scroll)
        panes = Gtk.Grid(column_spacing=16)
        panes.set_hexpand(True); panes.set_vexpand(True)
        panes.set_column_homogeneous(True)
        panes.attach(editor_frame, 0, 0, 1, 1)
        panes.attach(preview_frame, 1, 0, 1, 1)
        root.append(panes)
        self.status = Gtk.Label(label="Ready · 0 characters", xalign=0)
        self.status.add_css_class("dim-label"); self.status.set_hexpand(True)
        clear = Gtk.Button(label="Clear")
        clear.set_tooltip_text("Clear the Markdown source")
        clear.update_property([Gtk.AccessibleProperty.LABEL], ["Clear Markdown source"])
        clear.connect("clicked", self._clear)
        footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        footer.append(self.status); footer.append(clear); root.append(footer)
        self.set_canvas(root)
        self.editor.get_buffer().set_text(DEFAULT_MARKDOWN)
        provider = Gtk.CssProvider()
        provider.load_from_data(b"frame.editor-pane { border: 2px solid #8aa8b8; border-radius: 10px; padding: 8px; } label.markdown-title { font-size: 26px; font-weight: bold; } textview { padding: 14px; background: #ffffff; color: #20252a; } label.editor-empty-state { background: #f1f5f7; border-radius: 12px; padding: 18px 24px; color: #52636b; } button { min-height: 42px; border-radius: 19px; }")
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _render_preview(self, buffer):
        start, end = buffer.get_bounds()
        raw = buffer.get_text(start, end, False)
        text = raw.strip()
        self.preview.set_markup(render_markdown(text))
        self.editor_empty.set_visible(not text)
        self.status.set_text("Ready · %d characters" % len(raw))

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
