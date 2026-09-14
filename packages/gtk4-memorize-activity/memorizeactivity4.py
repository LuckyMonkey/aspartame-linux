"""Native GTK4 card-matching Memorize Activity."""

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class MemorizeActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("Memorize"); self.cards = [0, 1, 2, 3, 0, 1, 2, 3]; self.opened = []; self.matched = set(); self._build(); self._render()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        root.set_margin_top(28); root.set_margin_bottom(28); root.set_margin_start(32); root.set_margin_end(32)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Memorize card game"])
        title = Gtk.Label(label="Memorize", xalign=0); title.add_css_class("title-1"); root.append(title)
        root.append(Gtk.Label(label="Find each matching pair.", xalign=0))
        self.grid = Gtk.Grid(row_spacing=6, column_spacing=6); self.grid.set_halign(Gtk.Align.CENTER); root.append(self.grid)
        self.status = Gtk.Label(xalign=0); self.status.add_css_class("dim-label"); root.append(self.status)
        reset = Gtk.Button(label="New game"); reset.connect("clicked", self._reset); root.append(reset)
        self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"button { min-width: 62px; min-height: 62px; border-radius: 12px; font-size: 20px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _render(self):
        child = self.grid.get_first_child()
        while child is not None:
            nxt = child.get_next_sibling(); self.grid.remove(child); child = nxt
        for index, value in enumerate(self.cards):
            visible = index in self.opened or index in self.matched
            button = Gtk.Button(label=str(value + 1) if visible else "?"); button.update_property([Gtk.AccessibleProperty.LABEL], ["Card %d" % (index + 1)]); button.connect("clicked", self._flip, index); self.grid.attach(button, index % 4, index // 4, 1, 1)
        pairs = len(self.matched) // 2; self.status.set_text("Complete!" if pairs == 4 else "%d of 4 pairs matched" % pairs)

    def _flip(self, _button, index):
        if index in self.matched or index in self.opened: return
        self.opened.append(index)
        if len(self.opened) == 2:
            first, second = self.opened
            if self.cards[first] == self.cards[second]: self.matched.update(self.opened)
            self.opened = []
        self._render()

    def _reset(self, _button):
        self.cards = [0, 1, 2, 3, 0, 1, 2, 3]; self.opened = []; self.matched = set(); self._render()
