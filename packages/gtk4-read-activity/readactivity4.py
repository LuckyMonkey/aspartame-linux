"""Native GTK4 Read activity with a small offline document reader."""

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


DOCUMENT = {
    "title": "A Short Walk Through Aspartame",
    "author": "Aspartame Learning Library",
    "pages": (
        "Welcome to Read. This sample document is stored locally, so the activity is useful even when the network is unavailable.\n\nUse the search field to find a word, then use Previous and Next to move through the document.",
        "Sugar activities are small tools for learning, creating, and sharing. Read keeps the page simple: the document is the focus, while navigation stays close at hand.",
        "When a document is opened from the Journal, its title and reading position can be restored by the surrounding Sugar session. This preview uses the same readable, keyboard-friendly interaction.",
    ),
}


class ReadActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Read")
        self.page = 0
        self._build()
        self._update_page()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        root.set_margin_top(24); root.set_margin_bottom(24)
        root.set_margin_start(34); root.set_margin_end(34)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Read document viewer"])

        heading = Gtk.Label(label=DOCUMENT["title"], xalign=0)
        heading.add_css_class("title-1")
        root.append(heading)
        metadata = Gtk.Label(label=f'{DOCUMENT["author"]} · {len(DOCUMENT["pages"])} pages', xalign=0)
        metadata.add_css_class("dim-label")
        root.append(metadata)

        self.search = Gtk.SearchEntry(placeholder_text="Find in document")
        self.search.update_property([Gtk.AccessibleProperty.LABEL], ["Find in document"])
        self.search.connect("search-changed", self._search_changed)
        root.append(self.search)

        self.page_label = Gtk.Label(xalign=0)
        self.page_label.update_property([Gtk.AccessibleProperty.LABEL], ["Current page"])
        root.append(self.page_label)
        self.text = Gtk.Label(xalign=0, wrap=True, selectable=True)
        self.text.set_vexpand(True); self.text.set_valign(Gtk.Align.START)
        self.text.set_margin_top(20); self.text.set_margin_bottom(20)
        self.text.update_property([Gtk.AccessibleProperty.LABEL], ["Document text"])
        scroll = Gtk.ScrolledWindow(); scroll.set_child(self.text); scroll.set_vexpand(True)
        root.append(scroll)

        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.previous = Gtk.Button(label="Previous")
        self.previous.update_property([Gtk.AccessibleProperty.LABEL], ["Previous page"])
        self.previous.connect("clicked", self._move, -1)
        controls.append(self.previous)
        self.next = Gtk.Button(label="Next")
        self.next.update_property([Gtk.AccessibleProperty.LABEL], ["Next page"])
        self.next.connect("clicked", self._move, 1)
        controls.append(self.next)
        root.append(controls)
        self.set_canvas(root)

        provider = Gtk.CssProvider()
        provider.load_from_data(b"label { font-size: 16px; } button { min-height: 42px; border-radius: 19px; padding: 0 18px; }")
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _update_page(self):
        pages = DOCUMENT["pages"]
        self.page_label.set_text(f"Page {self.page + 1} of {len(pages)}")
        self.text.set_text(pages[self.page])
        self.previous.set_sensitive(self.page > 0)
        self.next.set_sensitive(self.page < len(pages) - 1)
        self._highlight_search()

    def _move(self, _button, delta):
        self.page = max(0, min(len(DOCUMENT["pages"]) - 1, self.page + delta))
        self._update_page()

    def _search_changed(self, _entry):
        self._highlight_search()

    def _highlight_search(self):
        query = self.search.get_text().strip().casefold()
        if query and query in DOCUMENT["pages"][self.page].casefold():
            self.page_label.set_text(f"Page {self.page + 1} of {len(DOCUMENT['pages'])} · match found")

