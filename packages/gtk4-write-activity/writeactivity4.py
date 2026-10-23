"""Native GTK4 Write Activity.

A port of GTK3 Write (sugarlabs/write-activity, an AbiWord front end):
character formatting (bold, italic, underline, superscript, subscript,
font, size, colour, highlight), paragraph styles, alignment, lists, images
from the Journal or files, find, undo/redo, and export to RTF, HTML, plain
text and PDF as new Journal objects.

Documents are saved as RTF, as GTK3 Write saves them, so either version
opens them. A document opened from HTML or plain text is saved back in
that format. The document model and formats live in :mod:`write_doc`.
"""

import base64
import tempfile
from pathlib import Path

from gi.repository import Gdk, GdkPixbuf, GLib, Gtk, Pango
from sugar4.activity import SimpleActivity

import write_doc
from write_doc import ALIGNS, EXPORTS, FLAGS, LISTS, SAVE_AS, STYLE_SIZES, STYLES

FONTS = ("Sans", "Serif", "Monospace")
SIZES = (8, 10, 12, 14, 16, 18, 24, 32, 48, 72)
COLORS = (("Automatic", None), ("Black", "#000000"), ("Red", "#c62828"), ("Green", "#2e7d32"),
          ("Blue", "#1565c0"), ("Orange", "#ef6c00"), ("Purple", "#6a1b9a"), ("Gray", "#616161"))
HIGHLIGHTS = (("No highlight", None), ("Yellow", "#fff176"), ("Green", "#c5e1a5"),
              ("Cyan", "#b2ebf2"), ("Pink", "#f8bbd0"))
STYLE_NAMES = ("Normal", "Heading 1", "Heading 2", "Heading 3", "Heading 4", "Block text", "Plain text")
ALIGN_NAMES = ("Left", "Center", "Right", "Fill")
LIST_NAMES = ("No list", "Bullet list", "Dashed list", "Numbered list", "Lower case list",
              "Upper case list")
FLAG_LABELS = (("bold", "Bold", "Ctrl+B"), ("italic", "Italic", "Ctrl+I"),
               ("underline", "Underline", "Ctrl+U"), ("super", "Superscript", ""),
               ("sub", "Subscript", ""))


class Journal:
    """The Journal, through the sugar4 datastore."""

    def images(self, limit=200):
        from sugar4.datastore import datastore
        entries, _count = datastore.find({}, sorting=["-timestamp"], limit=limit,
                                         properties=["uid", "title", "mime_type"])
        found = []
        for entry in entries:
            meta = entry.get_metadata()
            if str(meta.get("mime_type", "")).startswith("image/"):
                found.append((entry.object_id, str(meta.get("title") or "Image")))
            entry.destroy()
        return found

    def read(self, object_id):
        from sugar4.datastore import datastore
        entry = datastore.get(object_id)
        try:
            return Path(entry.get_file_path()).read_bytes()
        finally:
            entry.destroy()

    def export(self, title, mime_type, path):
        from sugar4.datastore import datastore
        entry = datastore.create()
        entry.metadata["title"] = title
        entry.metadata["mime_type"] = mime_type
        entry.file_path = str(path)
        datastore.write(entry, transfer_ownership=True)
        object_id = entry.object_id
        entry.destroy()
        return object_id


def png_from_file(path, max_width=640):
    """Any image GdkPixbuf reads, scaled to fit and re-encoded as PNG."""
    pixbuf = GdkPixbuf.Pixbuf.new_from_file(str(path))
    if pixbuf.get_width() > max_width:
        height = max(1, round(pixbuf.get_height() * max_width / pixbuf.get_width()))
        pixbuf = pixbuf.scale_simple(max_width, height, GdkPixbuf.InterpType.BILINEAR)
    ok, data = pixbuf.save_to_bufferv("png", [], [])
    if not ok:
        raise ValueError("cannot encode image")
    return bytes(data)


class WriteActivity(SimpleActivity):
    def __init__(self, activity_handle=None, journal=None):
        super().__init__(activity_handle)
        self.set_title("Write")
        self.journal = journal or Journal()
        self._images = {}          # key -> PNG bytes
        self._texture_keys = {}    # texture -> key
        self._pending = {}         # marks for the next typed text
        self._syncing = False
        self._loading = False
        self._save_mime = "application/rtf"
        self._build()
        self._sync_controls()

    # Layout

    def _button(self, label, tip, handler, *args, name=None):
        button = Gtk.Button(label=label)
        button.set_tooltip_text(tip)
        button.update_property([Gtk.AccessibleProperty.LABEL], [name or label])
        button.connect("clicked", handler, *args)
        return button

    def _dropdown(self, names, accessible, handler):
        dropdown = Gtk.DropDown.new_from_strings(list(names))
        dropdown.update_property([Gtk.AccessibleProperty.LABEL], [accessible])
        dropdown.set_tooltip_text(accessible)
        dropdown.connect("notify::selected", handler)
        return dropdown

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        root.set_margin_top(16); root.set_margin_bottom(16)
        root.set_margin_start(24); root.set_margin_end(24)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Write"])

        text_bar = Gtk.Box(spacing=6)
        for flag, label, key in FLAG_LABELS:
            tip = "%s%s" % (label, " (%s)" % key if key else "")
            text_bar.append(self._button(label, tip, self._toggle_flag, flag))
        self.font = self._dropdown(FONTS, "Font", self._font_changed)
        self.size = self._dropdown(["%d pt" % s for s in SIZES], "Font size", self._size_changed)
        self.color = self._dropdown([n for n, _c in COLORS], "Text color", self._color_changed)
        self.highlight = self._dropdown([n for n, _c in HIGHLIGHTS], "Highlight", self._highlight_changed)
        for widget in (self.font, self.size, self.color, self.highlight):
            text_bar.append(widget)
        root.append(text_bar)

        para_bar = Gtk.Box(spacing=6)
        self.style = self._dropdown(STYLE_NAMES, "Paragraph style", self._style_changed)
        self.align = self._dropdown(ALIGN_NAMES, "Alignment", self._align_changed)
        self.list = self._dropdown(LIST_NAMES, "List", self._list_changed)
        for widget in (self.style, self.align, self.list):
            para_bar.append(widget)
        para_bar.append(self._button("Image from Journal", "Insert an image from the Journal",
                                     self._show_picker))
        para_bar.append(self._button("Image file", "Insert an image file", self._image_file))
        para_bar.append(self._button("Undo", "Undo typing (Ctrl+Z)", self._undo))
        para_bar.append(self._button("Redo", "Redo typing (Ctrl+Shift+Z)", self._redo))
        root.append(para_bar)

        find_bar = Gtk.Box(spacing=6)
        self.find = Gtk.SearchEntry(placeholder_text="Find")
        self.find.update_property([Gtk.AccessibleProperty.LABEL], ["Find text"])
        self.find.connect("activate", lambda _e: self._find(None, 1))
        find_bar.append(self.find)
        find_bar.append(self._button("Find previous", "Find the previous match", self._find, -1))
        find_bar.append(self._button("Find next", "Find the next match", self._find, 1))
        spacer = Gtk.Box(hexpand=True)
        find_bar.append(spacer)
        for key, (title, _mime, _ext) in EXPORTS.items():
            find_bar.append(self._button("Export %s" % key.upper(), "Save a copy as %s in the Journal" % title,
                                         self._export, key))
        root.append(find_bar)

        self.picker = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        picker_head = Gtk.Box(spacing=8)
        picker_title = Gtk.Label(label="Journal images", xalign=0, hexpand=True)
        picker_title.add_css_class("heading")
        picker_head.append(picker_title)
        picker_head.append(self._button("Done", "Close the image list", self._hide_picker,
                                        name="Close image list"))
        self.picker.append(picker_head)
        self.picker_list = Gtk.FlowBox(selection_mode=Gtk.SelectionMode.NONE, max_children_per_line=4)
        self.picker_list.update_property([Gtk.AccessibleProperty.LABEL], ["Journal images"])
        self.picker.append(self.picker_list)
        self.picker.set_visible(False)
        root.append(self.picker)

        self.document = Gtk.TextView(wrap_mode=Gtk.WrapMode.WORD_CHAR, hexpand=True, vexpand=True)
        self.document.set_left_margin(18); self.document.set_right_margin(18)
        self.document.set_top_margin(14); self.document.set_bottom_margin(14)
        self.document.update_property([Gtk.AccessibleProperty.LABEL], ["Document text"])
        self.buffer = self.document.get_buffer()
        self.buffer.set_enable_undo(True)
        self._create_paragraph_tags()
        self.buffer.connect_after("insert-text", self._inserted)
        self.buffer.connect("mark-set", self._mark_set)
        self.buffer.connect("changed", self._changed)
        keys = Gtk.EventControllerKey()
        keys.connect("key-pressed", self._key)
        self.document.add_controller(keys)
        scroll = Gtk.ScrolledWindow(vexpand=True)
        scroll.set_child(self.document)
        frame = Gtk.Frame()
        frame.add_css_class("document-pane")
        frame.set_child(scroll)
        root.append(frame)

        self.status = Gtk.Label(label="Ready", xalign=0)
        self.status.add_css_class("dim-label")
        self.status.update_property([Gtk.AccessibleProperty.LABEL], ["Write status"])
        root.append(self.status)
        self.set_canvas(root)

        provider = Gtk.CssProvider()
        provider.load_from_data(
            b"frame.document-pane { border: 2px solid #8aa8b8; border-radius: 10px; }"
            b" textview { font-size: 12pt; } button { min-height: 36px; border-radius: 18px; }")
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    # Tags. Paragraph tags are created first so character tags win.

    def _create_paragraph_tags(self):
        table = self.buffer.get_tag_table()
        for style in STYLES[1:]:
            tag = Gtk.TextTag(name="style:" + style)
            if style in STYLE_SIZES:
                tag.props.weight = Pango.Weight.BOLD
                tag.props.size_points = STYLE_SIZES[style]
                tag.props.pixels_above_lines = 8
            elif style == "block":
                tag.props.left_margin = 58
                tag.props.right_margin = 58
            elif style == "plain":
                tag.props.family = "Monospace"
            table.add(tag)
        for align in ALIGNS[1:]:
            table.add(Gtk.TextTag(name="align:" + align, justification={
                "center": Gtk.Justification.CENTER, "right": Gtk.Justification.RIGHT,
                "fill": Gtk.Justification.FILL}[align]))
        for kind in LISTS[1:]:
            table.add(Gtk.TextTag(name="list:" + kind, left_margin=42))

    def _char_tag(self, key, value=True):
        name = key if value is True else "%s:%s" % (key, value)
        table = self.buffer.get_tag_table()
        tag = table.lookup(name)
        if tag is None:
            tag = Gtk.TextTag(name=name)
            if key == "bold":
                tag.props.weight = Pango.Weight.BOLD
            elif key == "italic":
                tag.props.style = Pango.Style.ITALIC
            elif key == "underline":
                tag.props.underline = Pango.Underline.SINGLE
            elif key == "super":
                tag.props.rise = 5 * Pango.SCALE
                tag.props.scale = 0.7
            elif key == "sub":
                tag.props.rise = -3 * Pango.SCALE
                tag.props.scale = 0.7
            elif key == "font":
                tag.props.family = value
            elif key == "size":
                tag.props.size_points = value
            elif key == "color":
                tag.props.foreground = value
            elif key == "highlight":
                tag.props.background = value
            table.add(tag)
        return tag

    @staticmethod
    def _split(tag):
        name = tag.props.name or ""
        key, _sep, value = name.partition(":")
        if key in FLAGS and not value:
            return key, True
        if key == "size":
            return key, int(value)
        if key in ("font", "color", "highlight"):
            return key, value
        return None, None

    def _marks_at(self, iterator):
        marks = {}
        for tag in iterator.get_tags():
            key, value = self._split(tag)
            if key:
                marks[key] = value
        return marks

    def _para_at(self, iterator):
        para = {"style": "normal", "align": "left", "list": None}
        for tag in iterator.get_tags():
            key, _sep, value = (tag.props.name or "").partition(":")
            if key in ("style", "align", "list") and value:
                para[key] = value
        return para

    # Selections and paragraphs

    def _bounds(self):
        bounds = self.buffer.get_selection_bounds()
        if bounds:
            return bounds[0], bounds[1]
        return None

    def _line_range(self, line):
        start = self.buffer.get_iter_at_line(line)
        start = start[1] if isinstance(start, tuple) else start
        end = start.copy()
        if not end.ends_line():
            end.forward_to_line_end()
        end_nl = end.copy()
        end_nl.forward_char()
        return start, end, end_nl

    def _selected_lines(self):
        bounds = self._bounds()
        if bounds:
            first, last = bounds[0].get_line(), bounds[1].get_line()
            if bounds[1].starts_line() and last > first:
                last -= 1
        else:
            first = last = self.buffer.get_iter_at_mark(self.buffer.get_insert()).get_line()
        return range(first, last + 1)

    def _set_para(self, line, key, value):
        start, _end, end_nl = self._line_range(line)
        choices = {"style": STYLES, "align": ALIGNS, "list": LISTS}[key]
        for other in choices[1:]:
            self.buffer.remove_tag_by_name("%s:%s" % (key, other), start, end_nl)
        if value and value != choices[0]:
            self.buffer.apply_tag_by_name("%s:%s" % (key, value), start, end_nl)

    # Formatting actions

    def _apply_mark(self, key, value):
        """Set a character mark on the selection, or on the next typed text."""
        bounds = self._bounds()
        if bounds is None:
            if value is None:
                self._pending[key] = None
            else:
                self._pending[key] = value
            return False
        start, end = bounds
        for tag in list(self._tags_with_key(key)):
            self.buffer.remove_tag(tag, start, end)
        if value is not None:
            self.buffer.apply_tag(self._char_tag(key, value), start, end)
        return True

    def _tags_with_key(self, key):
        found = []
        self.buffer.get_tag_table().foreach(lambda tag: found.append(tag) if self._split(tag)[0] == key else None)
        return found

    def _toggle_flag(self, _button, flag):
        bounds = self._bounds()
        if bounds is None:
            current = self._pending.get(flag, self._marks_at(self._cursor()).get(flag))
            self._pending[flag] = None if current else True
            self.status.set_text("%s %s for new text" % (flag.capitalize(), "off" if current else "on"))
            return
        start, end = bounds
        tag = self._char_tag(flag)
        iterator, everywhere = start.copy(), True
        while iterator.compare(end) < 0:
            if not iterator.has_tag(tag):
                everywhere = False
                break
            iterator.forward_char()
        if everywhere:
            self.buffer.remove_tag(tag, start, end)
        else:
            if flag in ("super", "sub"):
                self.buffer.remove_tag(self._char_tag("sub" if flag == "super" else "super"), start, end)
            self.buffer.apply_tag(tag, start, end)
        self.status.set_text("%s %s" % (dict((f, l) for f, l, _k in FLAG_LABELS)[flag],
                                        "removed" if everywhere else "applied"))

    def _font_changed(self, dropdown, _pspec):
        if not self._syncing:
            self._apply_mark("font", FONTS[dropdown.get_selected()])
            self.status.set_text("Font: %s" % FONTS[dropdown.get_selected()])

    def _size_changed(self, dropdown, _pspec):
        if not self._syncing:
            self._apply_mark("size", SIZES[dropdown.get_selected()])
            self.status.set_text("Size: %d pt" % SIZES[dropdown.get_selected()])

    def _color_changed(self, dropdown, _pspec):
        if not self._syncing:
            name, value = COLORS[dropdown.get_selected()]
            self._apply_mark("color", value)
            self.status.set_text("Text color: %s" % name)

    def _highlight_changed(self, dropdown, _pspec):
        if not self._syncing:
            name, value = HIGHLIGHTS[dropdown.get_selected()]
            self._apply_mark("highlight", value)
            self.status.set_text("Highlight: %s" % name)

    def _style_changed(self, dropdown, _pspec):
        if self._syncing:
            return
        for line in self._selected_lines():
            self._set_para(line, "style", STYLES[dropdown.get_selected()])
        self.status.set_text("Style: %s" % STYLE_NAMES[dropdown.get_selected()])

    def _align_changed(self, dropdown, _pspec):
        if self._syncing:
            return
        for line in self._selected_lines():
            self._set_para(line, "align", ALIGNS[dropdown.get_selected()])
        self.status.set_text("Alignment: %s" % ALIGN_NAMES[dropdown.get_selected()])

    def _list_changed(self, dropdown, _pspec):
        if self._syncing:
            return
        kind = LISTS[dropdown.get_selected()]
        for number, line in enumerate(self._selected_lines(), start=1):
            start, end, _nl = self._line_range(line)
            match = write_doc.MARKER.match(self.buffer.get_text(start, end, True))
            if match:
                cut = start.copy()
                cut.forward_chars(len(match.group(1)))
                self.buffer.delete(start, cut)
                start, end, _nl = self._line_range(line)
            if kind:
                self.buffer.insert(start, write_doc.marker(kind, number))
            self._set_para(line, "list", kind)
        self.status.set_text(LIST_NAMES[dropdown.get_selected()])

    # Typing

    def _cursor(self):
        return self.buffer.get_iter_at_mark(self.buffer.get_insert())

    def _inserted(self, buffer, location, text, length):
        if self._loading:
            return
        end = location.copy()
        start = location.copy()
        start.backward_chars(len(text))
        before = start.copy()
        # Typed text takes the formatting of the character before it.
        marks = self._marks_at(before) if before.backward_char() and before.get_char() != "\n" else {}
        marks.update(self._pending)
        for key in ("bold", "italic", "underline", "super", "sub", "font", "size", "color", "highlight"):
            for tag in self._tags_with_key(key):
                buffer.remove_tag(tag, start, end)
            if marks.get(key) is not None:
                buffer.apply_tag(self._char_tag(key, marks[key]), start, end)
        # New lines keep the paragraph formatting of the line they split.
        para = self._para_at(self._line_range(start.get_line())[0])
        for line in range(start.get_line(), end.get_line() + 1):
            for key in ("style", "align", "list"):
                self._set_para(line, key, para[key])

    def _key(self, _controller, keyval, _keycode, state):
        ctrl = state & Gdk.ModifierType.CONTROL_MASK
        if ctrl and keyval in (Gdk.KEY_b, Gdk.KEY_i, Gdk.KEY_u):
            self._toggle_flag(None, {Gdk.KEY_b: "bold", Gdk.KEY_i: "italic", Gdk.KEY_u: "underline"}[keyval])
            return True
        if keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter) and not ctrl:
            line = self._cursor().get_line()
            start, end, _nl = self._line_range(line)
            kind = self._para_at(start)["list"]
            text = self.buffer.get_text(start, end, True)
            if kind:
                match = write_doc.MARKER.match(text)
                if match and text == match.group(1):
                    # Enter on an empty item ends the list.
                    self.buffer.delete(start, end)
                    self._set_para(line, "list", None)
                    self._sync_controls()
                    return True
                number = sum(1 for n in range(line, -1, -1)
                             if self._para_at(self._line_range(n)[0])["list"] == kind) + 1
                self.buffer.insert_at_cursor("\n" + write_doc.marker(kind, number))
                return True
        return False

    def _mark_set(self, _buffer, _iter, mark):
        if mark.get_name() == "insert":
            self._pending = {}
            self._sync_controls()

    def _changed(self, _buffer):
        if not self._loading:
            self.status.set_text("%d characters" % self.buffer.get_char_count())

    def _sync_controls(self):
        iterator = self._cursor()
        before = iterator.copy()
        marks = self._marks_at(before) if before.backward_char() else self._marks_at(iterator)
        para = self._para_at(self._line_range(iterator.get_line())[0])
        self._syncing = True
        try:
            self.font.set_selected(FONTS.index(marks["font"]) if marks.get("font") in FONTS else 0)
            size = marks.get("size") or STYLE_SIZES.get(para["style"], 12)
            self.size.set_selected(SIZES.index(size) if size in SIZES else SIZES.index(12))
            self.color.set_selected(next((i for i, (_n, c) in enumerate(COLORS) if c == marks.get("color")), 0))
            self.highlight.set_selected(next((i for i, (_n, c) in enumerate(HIGHLIGHTS)
                                              if c == marks.get("highlight")), 0))
            self.style.set_selected(STYLES.index(para["style"]))
            self.align.set_selected(ALIGNS.index(para["align"]))
            self.list.set_selected(LISTS.index(para["list"]))
        finally:
            self._syncing = False

    def _undo(self, _button):
        if self.buffer.get_can_undo():
            self.buffer.undo()

    def _redo(self, _button):
        if self.buffer.get_can_redo():
            self.buffer.redo()

    def _find(self, _button, direction):
        needle = self.find.get_text()
        if not needle:
            self.status.set_text("Type text to find")
            return
        flags = Gtk.TextSearchFlags.CASE_INSENSITIVE
        bounds = self._bounds()
        if direction > 0:
            start = bounds[1] if bounds else self._cursor()
            found = start.forward_search(needle, flags, None) or \
                self.buffer.get_start_iter().forward_search(needle, flags, None)
        else:
            start = bounds[0] if bounds else self._cursor()
            found = start.backward_search(needle, flags, None) or \
                self.buffer.get_end_iter().backward_search(needle, flags, None)
        if not found:
            self.status.set_text("Not found: %s" % needle)
            return
        self.buffer.select_range(found[0], found[1])
        self.document.scroll_to_iter(found[0], 0.2, False, 0, 0)
        self.status.set_text("Found %s on line %d" % (needle, found[0].get_line() + 1))

    # Images

    def _insert_png(self, data, title):
        key = "image%d" % (len(self._images) + 1)
        while key in self._images:
            key += "x"
        self._images[key] = data
        texture = Gdk.Texture.new_from_bytes(GLib.Bytes.new(data))
        self._texture_keys[texture] = key
        self.buffer.insert_paintable(self._cursor(), texture)
        self.status.set_text("Inserted %s" % title)

    def _show_picker(self, _button):
        self.picker_list.remove_all()
        try:
            images = self.journal.images()
        except Exception as error:
            self.status.set_text("Cannot read the Journal: %s" % error)
            return
        for object_id, title in images:
            self.picker_list.append(self._button(title, "Insert this image", self._pick, object_id, title,
                                                 name="Insert %s" % title))
        if not images:
            self.picker_list.append(Gtk.Label(label="No images in the Journal yet."))
        self.picker.set_visible(True)

    def _hide_picker(self, _button):
        self.picker.set_visible(False)
        self.document.grab_focus()

    def _pick(self, _button, object_id, title):
        try:
            with tempfile.NamedTemporaryFile() as handle:
                handle.write(self.journal.read(object_id))
                handle.flush()
                data = png_from_file(handle.name)
        except (OSError, GLib.Error, ValueError) as error:
            self.status.set_text("Cannot insert %s: %s" % (title, error))
            return
        self._insert_png(data, title)
        self._hide_picker(None)

    def _image_file(self, _button):
        dialog = Gtk.FileDialog(title="Insert an image")
        dialog.open(self, None, self._image_chosen)

    def _image_chosen(self, dialog, result):
        try:
            chosen = dialog.open_finish(result)
            if chosen is None:
                return
            self._insert_png(png_from_file(chosen.get_path()), chosen.get_basename())
        except (GLib.Error, ValueError, TypeError) as error:
            self.status.set_text("Cannot insert image: %s" % error)

    # Document model

    def get_document(self):
        doc = {"format": write_doc.FORMAT, "images": {}, "paragraphs": []}
        for line in range(self.buffer.get_line_count()):
            start, end, _nl = self._line_range(line)
            p = dict(self._para_at(start), runs=[])
            iterator = start.copy()
            while iterator.compare(end) < 0:
                paintable = iterator.get_paintable()
                if paintable is not None:
                    key = self._texture_keys.get(paintable)
                    if key:
                        doc["images"][key] = base64.b64encode(self._images[key]).decode()
                        p["runs"].append({"image": key})
                    iterator.forward_char()
                    continue
                stop = iterator.copy()
                stop.forward_to_tag_toggle(None)
                if stop.compare(end) > 0:
                    stop = end.copy()
                # Images split text runs.
                probe = iterator.copy()
                while probe.compare(stop) < 0 and probe.get_paintable() is None:
                    probe.forward_char()
                stop = probe
                text = self.buffer.get_slice(iterator, stop, True)
                if text:
                    write_doc._append(p, text, self._marks_at(iterator))
                iterator = stop
            doc["paragraphs"].append(p)
        return write_doc.validate(doc)

    def set_document(self, doc):
        self._loading = True
        try:
            self.buffer.begin_irreversible_action()
            self.buffer.set_text("")
            self._images = {k: base64.b64decode(v) for k, v in doc["images"].items()}
            self._texture_keys = {}
            textures = {}
            for index, p in enumerate(doc["paragraphs"]):
                if index:
                    self.buffer.insert(self.buffer.get_end_iter(), "\n")
                for run in p["runs"]:
                    if "image" in run:
                        texture = textures.get(run["image"])
                        if texture is None:
                            texture = Gdk.Texture.new_from_bytes(GLib.Bytes.new(self._images[run["image"]]))
                            textures[run["image"]] = texture
                            self._texture_keys[texture] = run["image"]
                        self.buffer.insert_paintable(self.buffer.get_end_iter(), texture)
                        continue
                    tags = [self._char_tag(k, v) for k, v in run.get("marks", {}).items()]
                    self.buffer.insert_with_tags(self.buffer.get_end_iter(), run["text"], *tags)
                for key in ("style", "align", "list"):
                    self._set_para(index, key, p[key])
            self.buffer.place_cursor(self.buffer.get_start_iter())
            self.buffer.end_irreversible_action()
        finally:
            self._loading = False
        self._sync_controls()

    # Export

    def _title(self):
        meta = self.metadata or {}
        return str(meta.get("title") or "Write document")

    def _export(self, _button, key):
        title, mime_type, extension = EXPORTS[key]
        doc = self.get_document()
        path = Path(tempfile.mkstemp(prefix="write-export-", suffix=extension)[1])
        try:
            if key == "pdf":
                from write_pdf import write_pdf
                write_pdf(doc, path)
            elif key == "html":
                path.write_text(write_doc.write_html(doc, self._title()), encoding="utf-8")
            else:
                path.write_text({"rtf": write_doc.write_rtf, "txt": write_doc.write_txt}[key](doc),
                                encoding="utf-8")
            self.journal.export("%s (%s)" % (self._title(), key.upper()), mime_type, path)
        except Exception as error:
            path.unlink(missing_ok=True)
            self.status.set_text("Export failed: %s" % error)
            return
        self.status.set_text("Exported %s (%s) to the Journal" % (self._title(), key.upper()))

    # Journal

    def read_file(self, file_path):
        """Open RTF, HTML, plain text, or a Write 1/2 document; others raise."""
        raw = Path(file_path).read_text(encoding="utf-8")
        mime_type = (self.metadata or {}).get("mime_type", "")
        if mime_type == "text/plain":
            doc, source = write_doc.from_text(raw), "text/plain"
        else:
            doc, source = write_doc.loads(raw)
        self._save_mime = source if source in SAVE_AS else "application/rtf"
        self.set_document(doc)
        self.status.set_text("Opened %d paragraphs" % len(doc["paragraphs"]))

    def write_file(self, file_path):
        """Save as RTF, or in the HTML/plain-text format the document came in."""
        text = SAVE_AS[self._save_mime](self.get_document())
        if self.metadata is not None:
            self.metadata["mime_type"] = self._save_mime
        Path(file_path).write_text(text, encoding="utf-8")
