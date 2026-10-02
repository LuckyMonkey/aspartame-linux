"""Native GTK4 Write document Activity.

The toolkit owns the Journal object and calls :meth:`read_file` and
:meth:`write_file` around resume/save.

Payload format (append-only history):

* A document with no formatting is saved as plain UTF-8 text, exactly as the
  first GTK4 Write did, so older objects and plain-text tools keep working.
* A formatted document is saved as a small HTML file whose second line is the
  ``FORMAT_MARKER`` comment.  Only that marker switches the reader to HTML, so
  a plain document that merely contains HTML-looking text stays plain text.

Formatting covers what GTK3 Write users reach for first: bold, italic,
underline, strikethrough, two heading levels, and paragraph alignment.  Undo,
find, word count, zoom, and export to text or HTML are included.  Images,
tables, lists, fonts, ODT/PDF export, and collaboration remain unported.
"""

import html
from html.parser import HTMLParser
from pathlib import Path

from gi.repository import Gdk, Gio, GLib, Gtk, Pango
from sugar4.activity import SimpleActivity


FORMAT_MARKER = "<!-- aspartame-write-document v1 -->"
INLINE = ("bold", "italic", "underline", "strike")
INLINE_HTML = {"bold": "b", "italic": "i", "underline": "u", "strike": "s"}
HTML_INLINE = {value: key for key, value in INLINE_HTML.items()}
HTML_INLINE.update({"strong": "bold", "em": "italic", "del": "strike"})
BLOCKS = ("heading1", "heading2")
BLOCK_HTML = {"heading1": "h1", "heading2": "h2"}
ALIGNMENTS = ("center", "right")
ZOOM_STEPS = (0.8, 0.9, 1.0, 1.15, 1.3, 1.5, 1.75, 2.0)


class _DocumentParser(HTMLParser):
    """Turn our own HTML back into lines of (text, inline tags) plus a block."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lines = []
        self._inline = []
        self._current = None

    def handle_starttag(self, tag, attrs):
        if tag in ("p", "h1", "h2"):
            block = {"h1": "heading1", "h2": "heading2"}.get(tag)
            style = dict(attrs).get("style") or ""
            align = next((a for a in ALIGNMENTS if "text-align:%s" % a in style.replace(" ", "")), None)
            self._current = {"block": block, "align": align, "runs": []}
            self.lines.append(self._current)
        elif tag in HTML_INLINE:
            self._inline.append(HTML_INLINE[tag])

    def handle_endtag(self, tag):
        if tag in HTML_INLINE and HTML_INLINE[tag] in self._inline:
            self._inline.remove(HTML_INLINE[tag])
        elif tag in ("p", "h1", "h2"):
            self._current = None

    def handle_data(self, data):
        if self._current is None:
            if not data.strip():
                return
            self._current = {"block": None, "align": None, "runs": []}
            self.lines.append(self._current)
        self._current["runs"].append((data, frozenset(self._inline)))


class WriteActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Write")
        self._syncing = False
        self._typing_tags = set()
        self._zoom = ZOOM_STEPS.index(1.0)
        self._build()

    # -- interface -----------------------------------------------------

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        root.set_margin_top(24); root.set_margin_bottom(24)
        root.set_margin_start(30); root.set_margin_end(30)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Write document"])
        title = Gtk.Label(label="Write", xalign=0); title.add_css_class("title-1"); root.append(title)

        self.buffer = Gtk.TextBuffer(enable_undo=True)
        self._create_tags()
        self.document = Gtk.TextView(buffer=self.buffer)
        self.document.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.document.set_vexpand(True)
        self.document.set_left_margin(12); self.document.set_right_margin(12)
        self.document.set_top_margin(10); self.document.set_bottom_margin(10)
        self.document.update_property([Gtk.AccessibleProperty.LABEL], ["Document text"])

        root.append(self._format_bar())
        root.append(self._find_bar())
        scroll = Gtk.ScrolledWindow(); scroll.set_child(self.document); scroll.set_vexpand(True)
        root.append(scroll)

        self.status = Gtk.Label(label="Ready", xalign=0); self.status.add_css_class("dim-label")
        self.status.update_property([Gtk.AccessibleProperty.LABEL], ["Write status"])
        self.count = Gtk.Label(xalign=1); self.count.add_css_class("dim-label")
        self.count.set_hexpand(True)
        footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        footer.append(self.status); footer.append(self.count)
        root.append(footer)

        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        save = self._button("Save draft", "Save this document to the Journal", self._save)
        controls.append(save)
        export = Gtk.MenuButton(label="Export")
        export.set_tooltip_text("Save a copy as a text or web page file")
        export.update_property([Gtk.AccessibleProperty.LABEL], ["Export a copy"])
        menu = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        menu.append(self._button("Plain text (.txt)", "Export as plain text", self._export, "txt"))
        menu.append(self._button("Web page (.html)", "Export with formatting as HTML", self._export, "html"))
        popover = Gtk.Popover(); popover.set_child(menu); export.set_popover(popover)
        controls.append(export)
        controls.append(self._button("Clear", "Clear the page (Undo brings it back)", self._clear))
        root.append(controls)

        self.buffer.connect("changed", self._changed)
        self.buffer.connect_after("insert-text", self._inserted)
        self.buffer.connect("notify::cursor-position", self._cursor_moved)
        self._install_shortcuts(root)
        self.set_canvas(root)
        self._install_css()
        self._changed(self.buffer)

    def _button(self, label, tip, callback, *args):
        button = Gtk.Button(label=label)
        button.set_tooltip_text(tip)
        button.update_property([Gtk.AccessibleProperty.LABEL, Gtk.AccessibleProperty.DESCRIPTION], [label, tip])
        button.connect("clicked", lambda _b: callback(*args))
        return button

    def _create_tags(self):
        self.buffer.create_tag("bold", weight=Pango.Weight.BOLD)
        self.buffer.create_tag("italic", style=Pango.Style.ITALIC)
        self.buffer.create_tag("underline", underline=Pango.Underline.SINGLE)
        self.buffer.create_tag("strike", strikethrough=True)
        self.buffer.create_tag("heading1", scale=1.8, weight=Pango.Weight.BOLD, pixels_above_lines=8)
        self.buffer.create_tag("heading2", scale=1.4, weight=Pango.Weight.BOLD, pixels_above_lines=6)
        self.buffer.create_tag("center", justification=Gtk.Justification.CENTER)
        self.buffer.create_tag("right", justification=Gtk.Justification.RIGHT)

    def _format_bar(self):
        bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        bar.update_property([Gtk.AccessibleProperty.LABEL], ["Formatting"])
        bar.append(self._button("Undo", "Undo (Ctrl+Z)", self._undo))
        bar.append(self._button("Redo", "Redo (Ctrl+Shift+Z)", self._redo))
        bar.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        self.inline_buttons = {}
        for name, label, tip in (("bold", "B", "Bold (Ctrl+B)"), ("italic", "I", "Italic (Ctrl+I)"),
                                 ("underline", "U", "Underline (Ctrl+U)"), ("strike", "S", "Strikethrough")):
            button = Gtk.ToggleButton(label=label)
            button.set_tooltip_text(tip)
            button.update_property([Gtk.AccessibleProperty.LABEL], [tip.split(" (")[0]])
            button.connect("toggled", self._inline_toggled, name)
            self.inline_buttons[name] = button
            bar.append(button)
        bar.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        self.block_choice = Gtk.DropDown.new_from_strings(["Paragraph", "Heading 1", "Heading 2"])
        self.block_choice.set_tooltip_text("Paragraph style")
        self.block_choice.update_property([Gtk.AccessibleProperty.LABEL], ["Paragraph style"])
        self.block_choice.connect("notify::selected", self._block_chosen)
        bar.append(self.block_choice)
        self.align_choice = Gtk.DropDown.new_from_strings(["Align left", "Center", "Align right"])
        self.align_choice.set_tooltip_text("Paragraph alignment")
        self.align_choice.update_property([Gtk.AccessibleProperty.LABEL], ["Paragraph alignment"])
        self.align_choice.connect("notify::selected", self._align_chosen)
        bar.append(self.align_choice)
        bar.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        bar.append(self._button("A−", "Smaller text on screen (Ctrl+−)", self._zoom_by, -1))
        bar.append(self._button("A+", "Larger text on screen (Ctrl+=)", self._zoom_by, 1))
        bar.append(self._button("Find", "Find in document (Ctrl+F)", self._show_find))
        return bar

    def _find_bar(self):
        self.find_entry = Gtk.SearchEntry(placeholder_text="Find in document")
        self.find_entry.update_property([Gtk.AccessibleProperty.LABEL], ["Find in document"])
        self.find_entry.connect("activate", lambda _e: self._find(True))
        self.find_entry.connect("next-match", lambda _e: self._find(True))
        self.find_entry.connect("previous-match", lambda _e: self._find(False))
        self.find_entry.connect("stop-search", lambda _e: self._hide_find())
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        box.append(self.find_entry)
        box.append(self._button("Previous", "Previous match (Shift+Enter)", self._find, False))
        box.append(self._button("Next", "Next match (Enter)", self._find, True))
        box.append(self._button("Done", "Close find (Escape)", self._hide_find))
        self.find_revealer = Gtk.Revealer(child=box)
        return self.find_revealer

    def _install_shortcuts(self, widget):
        controller = Gtk.ShortcutController()
        controller.set_scope(Gtk.ShortcutScope.MANAGED)
        for accel, callback in (("<Control>b", lambda: self._toggle_inline("bold")),
                                ("<Control>i", lambda: self._toggle_inline("italic")),
                                ("<Control>u", lambda: self._toggle_inline("underline")),
                                ("<Control>z", self._undo), ("<Control><Shift>z", self._redo),
                                ("<Control>y", self._redo), ("<Control>f", self._show_find),
                                ("<Control>s", self._save), ("<Control>equal", lambda: self._zoom_by(1)),
                                ("<Control>plus", lambda: self._zoom_by(1)),
                                ("<Control>minus", lambda: self._zoom_by(-1))):
            action = Gtk.CallbackAction.new(lambda *_a, cb=callback: (cb(), True)[1])
            controller.add_shortcut(Gtk.Shortcut.new(Gtk.ShortcutTrigger.parse_string(accel), action))
        widget.add_controller(controller)

    def _install_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(b"textview { min-height: 360px; } button { min-height: 42px; border-radius: 19px; }")
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    # -- editing -------------------------------------------------------

    def _text(self):
        start, end = self.buffer.get_bounds()
        return self.buffer.get_text(start, end, False)

    def _changed(self, _buffer):
        text = self._text()
        words = len(text.split())
        self.count.set_text("%d word%s · %d character%s" % (
            words, "" if words == 1 else "s", len(text), "" if len(text) == 1 else "s"))

    def _inserted(self, buffer, location, text, length):
        if not self._typing_tags or self._syncing:
            return
        start = location.copy()
        start.backward_chars(len(text))
        for name in self._typing_tags:
            buffer.apply_tag_by_name(name, start, location)

    def _cursor_moved(self, buffer, _pspec):
        """Reflect the formatting at the cursor in the toolbar."""
        cursor = buffer.get_iter_at_mark(buffer.get_insert())
        probe = cursor.copy()
        if not probe.starts_line():
            probe.backward_char()
        self._syncing = True
        try:
            self._typing_tags = {name for name in INLINE if probe.has_tag(buffer.get_tag_table().lookup(name))}
            for name, button in self.inline_buttons.items():
                button.set_active(name in self._typing_tags)
            line = self._line_start(cursor)
            self.block_choice.set_selected(next((i + 1 for i, b in enumerate(BLOCKS) if self._line_has(line, b)), 0))
            self.align_choice.set_selected(next((i + 1 for i, a in enumerate(ALIGNMENTS) if self._line_has(line, a)), 0))
        finally:
            self._syncing = False

    def _line_has(self, line_start, name):
        return line_start.has_tag(self.buffer.get_tag_table().lookup(name))

    def _toggle_inline(self, name):
        button = self.inline_buttons[name]
        button.set_active(not button.get_active())

    def _inline_toggled(self, button, name):
        if self._syncing:
            return
        bounds = self.buffer.get_selection_bounds()
        if bounds:
            start, end = bounds
            if button.get_active():
                self.buffer.apply_tag_by_name(name, start, end)
            else:
                self.buffer.remove_tag_by_name(name, start, end)
        elif button.get_active():
            self._typing_tags.add(name)
        else:
            self._typing_tags.discard(name)
        self.document.grab_focus()

    @staticmethod
    def _line_start(where):
        start = where.copy()
        start.set_line_offset(0)
        return start

    def _selected_lines(self):
        bounds = self.buffer.get_selection_bounds()
        if bounds:
            start, end = bounds
        else:
            start = end = self.buffer.get_iter_at_mark(self.buffer.get_insert())
        start = self._line_start(start)
        end = end.copy()
        if not end.ends_line():
            end.forward_to_line_end()
        return start, end

    def _set_line_tag(self, family, chosen):
        if self._syncing:
            return
        start, end = self._selected_lines()
        for name in family:
            self.buffer.remove_tag_by_name(name, start, end)
        if chosen is not None:
            self.buffer.apply_tag_by_name(chosen, start, end)
        self.document.grab_focus()

    def _block_chosen(self, dropdown, _pspec):
        index = dropdown.get_selected()
        self._set_line_tag(BLOCKS, BLOCKS[index - 1] if index else None)

    def _align_chosen(self, dropdown, _pspec):
        index = dropdown.get_selected()
        self._set_line_tag(ALIGNMENTS, ALIGNMENTS[index - 1] if index else None)

    def _undo(self):
        if self.buffer.get_can_undo():
            self.buffer.undo()

    def _redo(self):
        if self.buffer.get_can_redo():
            self.buffer.redo()

    def _zoom_by(self, step):
        self._zoom = max(0, min(len(ZOOM_STEPS) - 1, self._zoom + step))
        provider = getattr(self, "_zoom_provider", None)
        if provider is None:
            provider = self._zoom_provider = Gtk.CssProvider()
            display = Gdk.Display.get_default()
            if display:
                Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        provider.load_from_data(("textview.write-page { font-size: %d%%; }" % round(ZOOM_STEPS[self._zoom] * 100)).encode())
        self.document.add_css_class("write-page")
        self.status.set_text("Zoom %d%%" % round(ZOOM_STEPS[self._zoom] * 100))

    def _show_find(self):
        self.find_revealer.set_reveal_child(True)
        self.find_entry.grab_focus()

    def _hide_find(self):
        self.find_revealer.set_reveal_child(False)
        self.document.grab_focus()

    def _find(self, forward):
        needle = self.find_entry.get_text()
        if not needle:
            return
        flags = Gtk.TextSearchFlags.CASE_INSENSITIVE
        bounds = self.buffer.get_selection_bounds()
        cursor = self.buffer.get_iter_at_mark(self.buffer.get_insert())
        if forward:
            origin = bounds[1] if bounds else cursor
            match = origin.forward_search(needle, flags, None) or self.buffer.get_start_iter().forward_search(needle, flags, None)
        else:
            origin = bounds[0] if bounds else cursor
            match = origin.backward_search(needle, flags, None) or self.buffer.get_end_iter().backward_search(needle, flags, None)
        if not match:
            self.status.set_text("“%s” was not found" % needle)
            return
        start, end = match
        self.buffer.select_range(start, end)
        self.document.scroll_to_iter(start, 0.2, False, 0, 0)
        self.status.set_text("Found “%s”" % needle)

    def _save(self):
        count = len(self._text())
        self.save()
        self.status.set_text(f"Draft saved ({count} characters)")

    def _clear(self):
        # delete() stays undoable; set_text() is irreversible in GTK4.
        start, end = self.buffer.get_bounds()
        self.buffer.begin_user_action()
        self.buffer.delete(start, end)
        self.buffer.end_user_action()
        self.status.set_text("Page cleared. Undo brings it back.")

    # -- serialization -------------------------------------------------

    def _lines(self):
        """Yield ``(block, align, [(text, inline tags)])`` for every line."""
        table = self.buffer.get_tag_table()
        for number in range(self.buffer.get_line_count()):
            found = self.buffer.get_iter_at_line(number)
            start = found[1] if isinstance(found, tuple) else found
            end = start.copy()
            if not end.ends_line():
                end.forward_to_line_end()
            block = next((b for b in BLOCKS if start.has_tag(table.lookup(b))), None) if not start.equal(end) else None
            align = next((a for a in ALIGNMENTS if start.has_tag(table.lookup(a))), None) if not start.equal(end) else None
            runs, here = [], start.copy()
            while here.compare(end) < 0:
                step = here.copy()
                step.forward_to_tag_toggle(None)
                if step.compare(end) > 0:
                    step = end.copy()
                tags = frozenset(n for n in INLINE if here.has_tag(table.lookup(n)))
                text = self.buffer.get_text(here, step, False)
                if runs and runs[-1][1] == tags:
                    runs[-1] = (runs[-1][0] + text, tags)
                else:
                    runs.append((text, tags))
                here = step
            yield block, align, runs

    def _is_formatted(self):
        return any(block or align or any(tags for _t, tags in runs) for block, align, runs in self._lines())

    def to_html(self, title="Write document"):
        body = []
        for block, align, runs in self._lines():
            element = BLOCK_HTML.get(block, "p")
            style = ' style="text-align:%s"' % align if align else ""
            inner = ""
            for text, tags in runs:
                piece = html.escape(text, quote=False)
                for name in INLINE:
                    if name in tags:
                        piece = "<%s>%s</%s>" % (INLINE_HTML[name], piece, INLINE_HTML[name])
                inner += piece
            body.append("<%s%s>%s</%s>" % (element, style, inner, element))
        return ("<!DOCTYPE html>\n%s\n<html><head><meta charset=\"utf-8\"><title>%s</title></head>\n<body>\n%s\n</body></html>\n"
                % (FORMAT_MARKER, html.escape(title), "\n".join(body)))

    def _load_html(self, text):
        parser = _DocumentParser()
        parser.feed(text.split("<body>", 1)[-1].rsplit("</body>", 1)[0])
        parser.close()
        self.buffer.set_text("")
        for index, line in enumerate(parser.lines):
            if index:
                self.buffer.insert(self.buffer.get_end_iter(), "\n")
            line_start = self.buffer.create_mark(None, self.buffer.get_end_iter(), True)
            for chunk, tags in line["runs"]:
                end = self.buffer.get_end_iter()
                if tags:
                    self.buffer.insert_with_tags_by_name(end, chunk, *sorted(tags))
                else:
                    self.buffer.insert(end, chunk)
            start = self.buffer.get_iter_at_mark(line_start)
            for name in (line["block"], line["align"]):
                if name:
                    self.buffer.apply_tag_by_name(name, start, self.buffer.get_end_iter())
            self.buffer.delete_mark(line_start)

    def read_file(self, file_path):
        """Restore the document from a Journal object (plain text or HTML)."""
        try:
            text = Path(file_path).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            self.status.set_text(f"Unable to open draft: {error}")
            return
        self._syncing = True
        try:
            # A resumed document starts with an empty undo history.
            self.buffer.set_enable_undo(False)
            if text.startswith("<!DOCTYPE html>\n" + FORMAT_MARKER):
                self._load_html(text)
            else:
                self.buffer.set_text(text)
            self.buffer.set_enable_undo(True)
        finally:
            self._syncing = False
        self.buffer.place_cursor(self.buffer.get_start_iter())
        self.status.set_text(f"Draft restored ({len(self._text())} characters)")

    def write_file(self, file_path):
        """Write plain text, or HTML once the document carries formatting."""
        formatted = self._is_formatted()
        payload = self.to_html() if formatted else self._text()
        metadata = getattr(self, "metadata", None)
        if metadata is not None:
            metadata["mime_type"] = "text/html" if formatted else "text/plain"
        try:
            Path(file_path).write_text(payload, encoding="utf-8")
        except OSError as error:
            self.status.set_text(f"Unable to save draft: {error}")
            raise

    def _export(self, kind):
        dialog = Gtk.FileDialog(title="Export a copy")
        dialog.set_initial_name("document." + kind)
        dialog.save(self, None, self._export_chosen, kind)

    def _export_chosen(self, dialog, result, kind):
        try:
            target = dialog.save_finish(result)
        except GLib.Error:
            return
        if target is None:
            return
        payload = self.to_html() if kind == "html" else self._text()
        try:
            target.replace_contents(payload.encode("utf-8"), None, False,
                                    Gio.FileCreateFlags.REPLACE_DESTINATION, None)
        except GLib.Error as error:
            self.status.set_text("Export failed: %s" % error.message)
            return
        self.status.set_text("Exported %s" % (target.get_basename() or "a copy"))
