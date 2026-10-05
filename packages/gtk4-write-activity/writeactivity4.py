"""Native GTK4 Write document Activity.

The toolkit owns the Journal object and calls :meth:`read_file` and
:meth:`write_file` around resume/save.  Keeping the document payload as UTF-8
text preserves the normal Sugar Activity file boundary without coupling this
Activity to datastore internals.
"""

import json
from pathlib import Path

from gi.repository import Gdk, Gtk, Pango
from sugar4.activity import SimpleActivity


class WriteActivity(SimpleActivity):
    FORMAT = "aspartame-write-v1"

    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("Write"); self._build()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10); root.set_margin_top(24); root.set_margin_bottom(24); root.set_margin_start(30); root.set_margin_end(30); root.set_hexpand(True); root.set_vexpand(True); root.update_property([Gtk.AccessibleProperty.LABEL], ["Write document"])
        title = Gtk.Label(label="Write", xalign=0); title.add_css_class("title-1"); root.append(title)
        self.document = Gtk.TextView(); self.document.set_wrap_mode(Gtk.WrapMode.WORD_CHAR); self.document.set_hexpand(True); self.document.set_vexpand(True); self.document.update_property([Gtk.AccessibleProperty.LABEL], ["Document text"])
        buffer = self.document.get_buffer()
        buffer.create_tag("bold", weight=Pango.Weight.BOLD)
        buffer.create_tag("italic", style=Pango.Style.ITALIC)
        buffer.create_tag("heading", weight=Pango.Weight.BOLD, scale=1.35)
        self._tag_names = ("bold", "italic", "heading")
        self._format_selection = None
        keys = Gtk.EventControllerKey(); keys.connect("key-pressed", self._format_key); self.document.add_controller(keys)
        format_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        format_label = Gtk.Label(label="Format", xalign=0); format_label.add_css_class("dim-label"); format_bar.append(format_label)
        select_all = Gtk.Button(label="Select all"); select_all.set_tooltip_text("Select the whole document for formatting"); select_all.update_property([Gtk.AccessibleProperty.LABEL], ["Select all document text"]); select_all.connect("clicked", self._select_all); format_bar.append(select_all)
        for label, tag, shortcut in (("Bold", "bold", "Ctrl+B"), ("Italic", "italic", "Ctrl+I"), ("Heading", "heading", "Ctrl+H")):
            button = Gtk.Button(label=label); button.set_tooltip_text(f"Apply {label.lower()} to selected text ({shortcut})"); button.update_property([Gtk.AccessibleProperty.LABEL], [f"Apply {label.lower()} formatting"]); button.connect("clicked", self._toggle_format, tag); format_bar.append(button)
        clear_format = Gtk.Button(label="Clear formatting"); clear_format.set_tooltip_text("Remove formatting from selected text"); clear_format.update_property([Gtk.AccessibleProperty.LABEL], ["Clear selected text formatting"]); clear_format.connect("clicked", self._clear_formatting); format_bar.append(clear_format)
        root.append(format_bar)
        document_scroll = Gtk.ScrolledWindow(); document_scroll.set_min_content_height(520); document_scroll.set_hexpand(True); document_scroll.set_vexpand(True); document_scroll.set_child(self.document)
        document_surface = Gtk.Overlay(); document_surface.set_hexpand(True); document_surface.set_vexpand(True); document_surface.set_child(document_scroll)
        self.empty_state = Gtk.Label(label="Start writing your document…", wrap=True); self.empty_state.add_css_class("editor-empty-state"); self.empty_state.set_halign(Gtk.Align.CENTER); self.empty_state.set_valign(Gtk.Align.CENTER); self.empty_state.set_can_target(False); self.empty_state.set_max_width_chars(42); document_surface.add_overlay(self.empty_state)
        buffer.connect("changed", self._document_changed)
        document_frame = Gtk.Frame(label="Document"); document_frame.add_css_class("document-pane"); document_frame.set_hexpand(True); document_frame.set_vexpand(True); document_frame.set_child(document_surface); root.append(document_frame)
        self.status = Gtk.Label(label="Ready", xalign=0); self.status.add_css_class("dim-label"); self.status.set_hexpand(True)
        footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8); footer.append(self.status)
        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        controls.set_halign(Gtk.Align.END)
        save = Gtk.Button(label="Save draft"); save.connect("clicked", self._save); controls.append(save)
        clear = Gtk.Button(label="Clear"); clear.connect("clicked", self._clear); controls.append(clear); footer.append(controls); root.append(footer)
        self.set_canvas(root); provider = Gtk.CssProvider(); provider.load_from_data(b"frame.document-pane { border: 2px solid #8aa8b8; border-radius: 10px; padding: 8px; } scrolledwindow { border: 1px solid #8aa8b8; border-radius: 8px; } textview { padding: 14px; } label.editor-empty-state { background: #f1f5f7; border-radius: 12px; padding: 18px 24px; color: #52636b; } button { min-height: 42px; border-radius: 19px; }"); display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _document_changed(self, _buffer):
        start, end = self.document.get_buffer().get_bounds()
        self.empty_state.set_visible(not self.document.get_buffer().get_text(start, end, False).strip())

    def _format_key(self, _controller, keyval, _keycode, state):
        if not state & Gdk.ModifierType.CONTROL_MASK:
            return False
        tag = {Gdk.KEY_b: "bold", Gdk.KEY_i: "italic", Gdk.KEY_h: "heading"}.get(keyval)
        if tag:
            self._toggle_format(None, tag)
            return True
        return False

    def _selection(self):
        buffer = self.document.get_buffer()
        bounds = buffer.get_selection_bounds()
        if len(bounds) == 3:
            selected, start, end = bounds
        else:
            start, end = bounds
            selected = start.get_offset() != end.get_offset()
        if selected:
            self._format_selection = (start.get_offset(), end.get_offset())
            return start, end
        if self._format_selection is not None:
            start_offset, end_offset = self._format_selection
            return buffer.get_iter_at_offset(start_offset), buffer.get_iter_at_offset(end_offset)
        start, end = buffer.get_bounds()
        if buffer.get_text(start, end, False):
            return start, end
        return None

    def _select_all(self, _button):
        buffer = self.document.get_buffer()
        start, end = buffer.get_bounds()
        self._format_selection = (start.get_offset(), end.get_offset())
        buffer.select_range(end, start)
        self.status.set_text("Selected all document text")

    def _toggle_format(self, _button, tag_name):
        try:
            selection = self._selection()
        except Exception as error:
            self.status.set_text(f"Formatting failed: {error}")
            return
        if selection is None:
            self.status.set_text("Select text before applying formatting")
            return
        start, end = selection
        buffer = self.document.get_buffer()
        self.status.set_text(f"Formatting {tag_name}…")
        try:
            buffer.apply_tag_by_name(tag_name, start, end)
        except Exception as error:
            self.status.set_text(f"Formatting failed: {error}")
            return
        self.status.set_text(f"Applied {tag_name} formatting")

    def _clear_formatting(self, _button):
        selection = self._selection()
        if selection is None:
            self.status.set_text("Select text before clearing formatting")
            return
        start, end = selection
        buffer = self.document.get_buffer()
        for tag_name in self._tag_names:
            buffer.remove_tag_by_name(tag_name, start, end)
        self.status.set_text("Formatting cleared")

    def _format_spans(self):
        buffer = self.document.get_buffer()
        spans = []
        for tag_name in self._tag_names:
            tag = buffer.get_tag_table().lookup(tag_name)
            iterator = buffer.get_start_iter()
            span_start = None
            while not iterator.is_end():
                if iterator.has_tag(tag):
                    if span_start is None:
                        span_start = iterator.get_offset()
                elif span_start is not None:
                    spans.append({"start": span_start, "end": iterator.get_offset(), "tags": [tag_name]})
                    span_start = None
                iterator.forward_char()
            if span_start is not None:
                spans.append({"start": span_start, "end": buffer.get_end_iter().get_offset(), "tags": [tag_name]})
        spans.sort(key=lambda span: (span["start"], span["end"], span["tags"]))
        return spans

    def _set_document(self, text, spans=()):
        buffer = self.document.get_buffer()
        buffer.set_text(text)
        for span in spans:
            try:
                start = max(0, min(len(text), int(span["start"])))
                end = max(start, min(len(text), int(span["end"])))
                for tag_name in span.get("tags", ()):
                    if tag_name in self._tag_names and start < end:
                        buffer.apply_tag_by_name(tag_name, buffer.get_iter_at_offset(start), buffer.get_iter_at_offset(end))
            except (KeyError, TypeError, ValueError):
                continue
        self._document_changed(buffer)

    def _save(self, _button):
        start, end = self.document.get_buffer().get_bounds()
        count = len(self.document.get_buffer().get_text(start, end, False))
        self.save()
        self.status.set_text(f"Draft saved ({count} characters)")

    def _clear(self, _button): self._format_selection = None; self._set_document(""); self.status.set_text("Ready")

    def read_file(self, file_path):
        """Restore the document body from a Journal object."""
        try:
            raw = Path(file_path).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            self.status.set_text(f"Unable to open draft: {error}")
            return
        text = raw
        spans = ()
        try:
            payload = json.loads(raw) if raw.lstrip().startswith("{") else None
            if isinstance(payload, dict) and payload.get("format") == self.FORMAT and isinstance(payload.get("text"), str):
                text = payload["text"]
                spans = payload.get("spans", ()) if isinstance(payload.get("spans", ()), list) else ()
        except (TypeError, ValueError, json.JSONDecodeError):
            pass
        self._format_selection = None
        self._set_document(text, spans)
        self.status.set_text(f"Draft restored ({len(text)} characters)")

    def write_file(self, file_path):
        """Write the current document body for the Journal datastore."""
        start, end = self.document.get_buffer().get_bounds()
        text = self.document.get_buffer().get_text(start, end, False)
        spans = self._format_spans()
        try:
            if spans:
                payload = {"format": self.FORMAT, "spans": spans, "text": text}
                Path(file_path).write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
            else:
                Path(file_path).write_text(text, encoding="utf-8")
        except OSError as error:
            self.status.set_text(f"Unable to save draft: {error}")
            raise
