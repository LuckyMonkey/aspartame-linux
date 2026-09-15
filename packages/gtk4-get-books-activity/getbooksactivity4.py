"""Offline GTK4 catalog for the Sugar Get Books activity.

The original activity queried remote OPDS catalogs.  The modern preview keeps
the same useful interaction (find a title, inspect its metadata, and open a
reading view) without making network access part of the shell smoke test.
"""

import json
from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


BOOKS = (
    {"title": "The Wonderful Wizard of Oz", "author": "L. Frank Baum", "year": "1900", "description": "Dorothy travels through a strange and colorful land to find her way home."},
    {"title": "The Secret Garden", "author": "Frances Hodgson Burnett", "year": "1911", "description": "A locked garden becomes a place of friendship, curiosity, and renewal."},
    {"title": "Twenty Thousand Leagues Under the Sea", "author": "Jules Verne", "year": "1870", "description": "An imaginative voyage beneath the oceans aboard the Nautilus."},
    {"title": "Aesop's Fables", "author": "Aesop", "year": "600 BCE", "description": "Short stories that invite readers to think about choices and consequences."},
    {"title": "The Adventures of Tom Sawyer", "author": "Mark Twain", "year": "1876", "description": "Tom finds mischief, friendship, and adventure along the Mississippi River."},
    {"title": "Journey to the Center of the Earth", "author": "Jules Verne", "year": "1864", "description": "A scientific expedition discovers a world hidden deep beneath the surface."},
)


class GetBooksActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Get Books")
        self._build()
        self._show_books(BOOKS)

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        root.set_margin_top(24); root.set_margin_bottom(24)
        root.set_margin_start(30); root.set_margin_end(30)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Get Books catalog"])

        title = Gtk.Label(label="Get Books", xalign=0)
        title.add_css_class("title-1")
        root.append(title)
        subtitle = Gtk.Label(label="Browse a small offline library. Select a book to read its description.", xalign=0)
        subtitle.add_css_class("dim-label")
        root.append(subtitle)

        self.search = Gtk.SearchEntry(placeholder_text="Search titles or authors")
        self.search.update_property([Gtk.AccessibleProperty.LABEL], ["Search books"])
        self.search.connect("search-changed", self._search_changed)
        root.append(self.search)

        self.results = Gtk.ListBox(selection_mode=Gtk.SelectionMode.SINGLE)
        self.results.set_vexpand(True)
        self.results.set_placeholder(Gtk.Label(label="No matching books."))
        self.results.update_property([Gtk.AccessibleProperty.LABEL], ["Book results"])
        self.results.connect("row-selected", self._row_selected)
        scroll = Gtk.ScrolledWindow(); scroll.set_child(self.results); scroll.set_vexpand(True)
        root.append(scroll)

        self.details = Gtk.Label(label="Select a book to see details.", xalign=0, wrap=True)
        self.details.add_css_class("book-details")
        self.details.update_property([Gtk.AccessibleProperty.LABEL], ["Book details"])
        root.append(self.details)
        self.read = Gtk.Button(label="Read selected book")
        self.read.set_sensitive(False)
        self.read.update_property([Gtk.AccessibleProperty.LABEL], ["Read selected book"])
        self.read.connect("clicked", self._read_selected)
        root.append(self.read)
        self.set_canvas(root)

        provider = Gtk.CssProvider()
        provider.load_from_data(b"listboxrow { padding: 12px; } .book-title { font-weight: bold; } .book-details { padding: 10px 0; } button { min-height: 42px; border-radius: 19px; }")
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _show_books(self, books):
        while (row := self.results.get_row_at_index(0)) is not None:
            self.results.remove(row)
        for book in books:
            row = Gtk.ListBoxRow()
            row.book = book
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
            label = Gtk.Label(label=book["title"], xalign=0); label.add_css_class("book-title")
            author = Gtk.Label(label=f'{book["author"]} · {book["year"]}', xalign=0)
            author.add_css_class("dim-label")
            box.append(label); box.append(author); row.set_child(box)
            self.results.append(row)
        self.details.set_text("Select a book to see details.")
        self.read.set_sensitive(False)

    def _search_changed(self, entry):
        query = entry.get_text().strip().casefold()
        self._show_books(tuple(book for book in BOOKS if not query or query in book["title"].casefold() or query in book["author"].casefold()))

    def _row_selected(self, _list, row):
        if row is None:
            self.details.set_text("Select a book to see details."); self.read.set_sensitive(False); return
        book = row.book
        self._selected_title = book["title"]
        self.details.set_text(f'{book["title"]}\n{book["author"]} · {book["year"]}\n\n{book["description"]}')
        self.read.set_sensitive(True)

    def _read_selected(self, _button):
        row = self.results.get_selected_row()
        if row is not None:
            self.details.set_text(f'Reading preview: {row.book["title"]}\n\n{row.book["description"]}\n\nThis offline catalog does not download books.')

    def read_file(self, file_path):
        """Restore catalog query and selected book from a JSON Journal object."""
        try:
            payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
            query = str(payload.get("query", "")) if isinstance(payload, dict) else ""
            selected = str(payload.get("selected", "")) if isinstance(payload, dict) else ""
        except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
            query, selected = "", ""
        self.search.set_text(query)
        row = next((self.results.get_row_at_index(i) for i in range(len(BOOKS)) if self.results.get_row_at_index(i) is not None and getattr(self.results.get_row_at_index(i), "book", {}).get("title") == selected), None)
        if row is not None:
            self.results.select_row(row)

    def write_file(self, file_path):
        """Save catalog query and selected book as a JSON Journal object."""
        Path(file_path).write_text(json.dumps({"query": self.search.get_text(), "selected": getattr(self, "_selected_title", "")}, sort_keys=True) + "\n", encoding="utf-8")
