"""Native GTK4 Read activity with Journal-backed document reading.

As in GTK3 Read, the Journal object *is* the document.  Supported formats:

* **Text** — UTF-8, pages separated by form feeds (the first GTK4 format).
* **PDF** — rendered page by page with Poppler (``Poppler 0.18`` GI, pulled in
  by the image's GTK3 Read package).  Without Poppler the document is kept
  intact and the page says what is missing.
* **EPUB** — read with the standard library: the spine's XHTML chapters are
  turned into readable text pages.  Images and styling are not shown.

``write_file`` never converts a document: PDF and EPUB bytes are written back
unchanged, text is written as text.  The reading position is kept in the
Journal metadata as ``Read_current_page``, the key GTK3 Read uses.
Annotations, bookmarks, text-to-speech, and collaboration remain unported.
"""

import posixpath
import re
import zipfile
from html.parser import HTMLParser
from pathlib import Path

import gi
from gi.repository import Gdk, GLib, Gtk

from sugar4.activity import SimpleActivity

try:
    gi.require_version("Poppler", "0.18")
    from gi.repository import Poppler
    import cairo
except (ValueError, ImportError):  # Poppler or pycairo is not installed
    Poppler = None


DOCUMENT = {
    "title": "A Short Walk Through Aspartame",
    "author": "Aspartame Learning Library",
    "pages": (
        "Welcome to Read. This sample document is stored locally, so the activity is useful even when the network is unavailable.\n\nUse the search field to find a word, then use Previous and Next to move through the document.",
        "Sugar activities are small tools for learning, creating, and sharing. Read keeps the page simple: the document is the focus, while navigation stays close at hand.",
        "When a document is opened from the Journal, its title and reading position can be restored by the surrounding Sugar session. This preview uses the same readable, keyboard-friendly interaction.",
    ),
}
PAGE_KEY = "Read_current_page"
EPUB_PAGE_CHARS = 3000
ZOOM_STEPS = (0.75, 1.0, 1.25, 1.5, 2.0, 2.5)


class _TextExtractor(HTMLParser):
    BLOCKS = {"p", "div", "br", "h1", "h2", "h3", "h4", "h5", "h6", "li", "tr", "section", "blockquote"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.title, self._skip, self._in_title = [], "", 0, False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "head"):
            self._skip += 1
        if tag == "title":
            self._in_title = True
        if tag in self.BLOCKS:
            self.parts.append("\n\n" if tag != "br" else "\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "head") and self._skip:
            self._skip -= 1
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        elif not self._skip:
            self.parts.append(data)

    def text(self):
        text = re.sub(r"[ \t\r\f\v]+", " ", "".join(self.parts))
        return re.sub(r"\n\s*\n+", "\n\n", text).strip()


def epub_pages(data_path):
    """Return (title, author, pages) for an EPUB file, or raise ValueError."""
    with zipfile.ZipFile(data_path) as book:
        container = book.read("META-INF/container.xml").decode("utf-8", "replace")
        match = re.search(r'full-path="([^"]+)"', container)
        if not match:
            raise ValueError("EPUB has no package document")
        opf_path = match.group(1)
        opf = book.read(opf_path).decode("utf-8", "replace")
        base = posixpath.dirname(opf_path)
        manifest = {m.group(1): m.group(2) for m in re.finditer(
            r'<item\b[^>]*\bid="([^"]+)"[^>]*\bhref="([^"]+)"', opf)}
        manifest.update({m.group(2): m.group(1) for m in re.finditer(
            r'<item\b[^>]*\bhref="([^"]+)"[^>]*\bid="([^"]+)"', opf)})
        title = re.search(r"<dc:title[^>]*>(.*?)</dc:title>", opf, re.S)
        author = re.search(r"<dc:creator[^>]*>(.*?)</dc:creator>", opf, re.S)
        pages = []
        for idref in re.findall(r'<itemref\b[^>]*\bidref="([^"]+)"', opf):
            href = manifest.get(idref)
            if not href:
                continue
            name = posixpath.normpath(posixpath.join(base, href.split("#")[0]))
            try:
                extractor = _TextExtractor()
                extractor.feed(book.read(name).decode("utf-8", "replace"))
            except KeyError:
                continue
            chapter = extractor.text()
            while chapter:
                if len(chapter) <= EPUB_PAGE_CHARS:
                    pages.append(chapter)
                    break
                cut = chapter.rfind("\n\n", 0, EPUB_PAGE_CHARS)
                cut = cut if cut > EPUB_PAGE_CHARS // 3 else EPUB_PAGE_CHARS
                pages.append(chapter[:cut].strip())
                chapter = chapter[cut:].strip()
        if not pages:
            raise ValueError("EPUB has no readable chapters")
        clean = lambda m: re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else ""
        return clean(title) or "Untitled book", clean(author), pages


class ReadActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Read")
        self.kind = "text"
        self.pages = list(DOCUMENT["pages"])
        self.raw = None
        self.pdf = None
        self.page = 0
        self._zoom = ZOOM_STEPS.index(1.0)
        self._build()
        self._set_heading(DOCUMENT["title"], DOCUMENT["author"])
        self._update_page()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        root.set_margin_top(24); root.set_margin_bottom(24)
        root.set_margin_start(34); root.set_margin_end(34)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Read document viewer"])

        self.heading = Gtk.Label(xalign=0, wrap=True)
        self.heading.add_css_class("title-1")
        root.append(self.heading)
        self.metadata_label = Gtk.Label(xalign=0)
        self.metadata_label.add_css_class("dim-label")
        root.append(self.metadata_label)

        find = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.search = Gtk.SearchEntry(placeholder_text="Find in document")
        self.search.set_hexpand(True)
        self.search.update_property([Gtk.AccessibleProperty.LABEL], ["Find in document"])
        self.search.connect("search-changed", self._search_changed)
        self.search.connect("activate", lambda _e: self._find(1))
        self.search.connect("next-match", lambda _e: self._find(1))
        self.search.connect("previous-match", lambda _e: self._find(-1))
        find.append(self.search)
        find_next = Gtk.Button(label="Find next")
        find_next.update_property([Gtk.AccessibleProperty.LABEL], ["Find next page with a match"])
        find_next.connect("clicked", lambda _b: self._find(1))
        find.append(find_next)
        root.append(find)

        self.page_label = Gtk.Label(xalign=0)
        self.page_label.update_property([Gtk.AccessibleProperty.LABEL], ["Current page"])
        root.append(self.page_label)
        self.stack = Gtk.Stack()
        self.stack.set_vexpand(True)
        self.text = Gtk.Label(xalign=0, wrap=True, selectable=True)
        self.text.set_vexpand(True); self.text.set_valign(Gtk.Align.START)
        self.text.set_margin_top(20); self.text.set_margin_bottom(20)
        self.text.update_property([Gtk.AccessibleProperty.LABEL], ["Document text"])
        text_scroll = Gtk.ScrolledWindow(); text_scroll.set_child(self.text)
        self.stack.add_named(text_scroll, "text")
        self.picture = Gtk.Picture(can_shrink=False)
        self.picture.update_property([Gtk.AccessibleProperty.LABEL], ["Document page"])
        picture_scroll = Gtk.ScrolledWindow(); picture_scroll.set_child(self.picture)
        self.stack.add_named(picture_scroll, "picture")
        root.append(self.stack)

        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.previous = Gtk.Button(label="Previous")
        self.previous.update_property([Gtk.AccessibleProperty.LABEL], ["Previous page"])
        self.previous.connect("clicked", self._move, -1)
        controls.append(self.previous)
        self.next = Gtk.Button(label="Next")
        self.next.update_property([Gtk.AccessibleProperty.LABEL], ["Next page"])
        self.next.connect("clicked", self._move, 1)
        controls.append(self.next)
        self.goto = Gtk.SpinButton.new_with_range(1, 1, 1)
        self.goto.set_tooltip_text("Go to page")
        self.goto.update_property([Gtk.AccessibleProperty.LABEL], ["Go to page"])
        self.goto.connect("value-changed", self._goto)
        controls.append(self.goto)
        for label, name, step in (("A−", "Smaller", -1), ("A+", "Larger", 1)):
            button = Gtk.Button(label=label)
            button.update_property([Gtk.AccessibleProperty.LABEL], [name])
            button.connect("clicked", lambda _b, s=step: self._zoom_by(s))
            controls.append(button)
        root.append(controls)
        self.set_canvas(root)

        provider = Gtk.CssProvider()
        provider.load_from_data(b"label { font-size: 16px; } button { min-height: 42px; border-radius: 19px; padding: 0 18px; }")
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self._zoom_provider = Gtk.CssProvider()
        if display:
            Gtk.StyleContext.add_provider_for_display(display, self._zoom_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def _set_heading(self, title, author):
        self.heading.set_text(title)
        count = self._page_count()
        detail = "%d page%s" % (count, "" if count == 1 else "s")
        self.metadata_label.set_text("%s · %s" % (author, detail) if author else detail)

    def _page_count(self):
        return self.pdf.get_n_pages() if self.pdf is not None else len(self.pages)

    def _page_text(self, index):
        if self.pdf is not None:
            return self.pdf.get_page(index).get_text() or ""
        return self.pages[index]

    def _update_page(self):
        count = self._page_count()
        self.page = max(0, min(self.page, count - 1))
        self.page_label.set_text(f"Page {self.page + 1} of {count}")
        if self.pdf is not None:
            self._render_pdf_page()
            self.stack.set_visible_child_name("picture")
        else:
            self.text.set_text(self.pages[self.page])
            self.stack.set_visible_child_name("text")
        self.previous.set_sensitive(self.page > 0)
        self.next.set_sensitive(self.page < count - 1)
        self.goto.set_range(1, max(1, count))
        if int(self.goto.get_value()) != self.page + 1:
            self.goto.set_value(self.page + 1)
        metadata = getattr(self, "metadata", None)
        if metadata is not None:
            metadata[PAGE_KEY] = str(self.page)
        self._highlight_search()

    def _render_pdf_page(self):
        page = self.pdf.get_page(self.page)
        width, height = page.get_size()
        scale = 1.4 * ZOOM_STEPS[self._zoom]
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, max(1, int(width * scale)), max(1, int(height * scale)))
        context = cairo.Context(surface)
        context.set_source_rgb(1, 1, 1); context.paint()
        context.scale(scale, scale)
        page.render(context)
        surface.flush()
        texture = Gdk.MemoryTexture.new(surface.get_width(), surface.get_height(),
                                        Gdk.MemoryFormat.B8G8R8A8_PREMULTIPLIED,
                                        GLib.Bytes.new(bytes(surface.get_data())), surface.get_stride())
        self.picture.set_paintable(texture)
        self.picture.update_property([Gtk.AccessibleProperty.DESCRIPTION], [self._page_text(self.page)[:2000]])

    def _move(self, _button, delta):
        self.page = max(0, min(self._page_count() - 1, self.page + delta))
        self._update_page()

    def _goto(self, spin):
        target = int(spin.get_value()) - 1
        if target != self.page:
            self.page = target
            self._update_page()

    def _zoom_by(self, step):
        self._zoom = max(0, min(len(ZOOM_STEPS) - 1, self._zoom + step))
        self._zoom_provider.load_from_data(
            (".read-text { font-size: %dpx; }" % round(16 * ZOOM_STEPS[self._zoom])).encode())
        self.text.add_css_class("read-text")
        if self.pdf is not None:
            self._render_pdf_page()

    def _search_changed(self, _entry):
        self._highlight_search()

    def _highlight_search(self):
        query = self.search.get_text().strip().casefold()
        if query and query in self._page_text(self.page).casefold():
            self.page_label.set_text(f"Page {self.page + 1} of {self._page_count()} · match found")

    def _find(self, direction):
        query = self.search.get_text().strip().casefold()
        if not query:
            return
        count = self._page_count()
        for offset in range(1, count + 1):
            index = (self.page + direction * offset) % count
            if query in self._page_text(index).casefold():
                self.page = index
                self._update_page()
                return
        self.page_label.set_text(f"Page {self.page + 1} of {count} · “{self.search.get_text().strip()}” not found")

    # -- Journal -------------------------------------------------------

    def _restore_position(self):
        metadata = getattr(self, "metadata", None)
        try:
            self.page = int(metadata.get(PAGE_KEY, 0)) if metadata is not None else 0
        except (TypeError, ValueError, AttributeError):
            self.page = 0

    def read_file(self, file_path):
        """Open the Journal object as text, PDF, or EPUB."""
        try:
            data = Path(file_path).read_bytes()
        except OSError:
            return
        if data.startswith(b"%PDF"):
            self._open_pdf(file_path, data)
        elif data.startswith(b"PK") and b"application/epub+zip" in data[:200]:
            self._open_epub(file_path, data)
        else:
            try:
                text = data.decode("utf-8")
            except UnicodeError:
                return
            if not text.strip():
                return
            self.kind, self.raw, self.pdf = "text", None, None
            self.pages = text.split("\f")
            first = self.pages[0].strip().split("\n", 1)[0]
            self._set_heading(first[:80] or "Journal text", "")
        self._restore_position()
        self._update_page()

    def _open_pdf(self, file_path, data):
        self.kind, self.raw = "pdf", data
        if Poppler is None:
            self.pdf = None
            self.pages = ["This PDF is kept safely in the Journal, but it cannot be shown "
                          "because Poppler for GTK4 is not installed."]
            self._set_heading("PDF document", "")
            return
        try:
            self.pdf = Poppler.Document.new_from_bytes(GLib.Bytes.new(data), None)
        except GLib.Error as error:
            self.pdf = None
            self.pages = ["This PDF could not be opened: %s" % error.message]
            self._set_heading("PDF document", "")
            return
        self._set_heading(self.pdf.get_title() or Path(file_path).stem or "PDF document",
                          self.pdf.get_author() or "")

    def _open_epub(self, file_path, data):
        self.kind, self.raw, self.pdf = "epub", data, None
        try:
            title, author, self.pages = epub_pages(file_path)
        except (OSError, ValueError, KeyError, zipfile.BadZipFile):
            self.pages = ["This book is kept safely in the Journal, but its chapters could not be read."]
            title, author = "EPUB book", ""
        self._set_heading(title, author)

    def write_file(self, file_path):
        """Write the document back without converting it."""
        if self.raw is not None:
            Path(file_path).write_bytes(self.raw)
        else:
            Path(file_path).write_text("\f".join(self.pages), encoding="utf-8")
        metadata = getattr(self, "metadata", None)
        if metadata is not None:
            metadata[PAGE_KEY] = str(self.page)
