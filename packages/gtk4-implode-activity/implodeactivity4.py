"""Native GTK4 Implode matching-block puzzle Activity."""

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class ImplodeActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("Implode"); self.blocks = [0, 0, 1, 1, 2, 2, 0, 1, 2]; self._build(); self._render()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        root.set_margin_top(30); root.set_margin_bottom(30); root.set_margin_start(34); root.set_margin_end(34)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Implode puzzle"])
        title = Gtk.Label(label="Implode", xalign=0); title.add_css_class("title-1"); root.append(title)
        root.append(Gtk.Label(label="Click a block to remove its matching group.", xalign=0))
        self.grid = Gtk.Grid(row_spacing=4, column_spacing=4); self.grid.set_halign(Gtk.Align.CENTER); root.append(self.grid)
        self.status = Gtk.Label(xalign=0); self.status.add_css_class("dim-label"); root.append(self.status)
        reset = Gtk.Button(label="Reset puzzle"); reset.connect("clicked", self._reset); root.append(reset)
        self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"button { min-width: 72px; min-height: 48px; border-radius: 16px; font-size: 18px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _render(self):
        child = self.grid.get_first_child()
        while child is not None:
            nxt = child.get_next_sibling(); self.grid.remove(child); child = nxt
        colours = ("#e45756", "#57b8ff", "#f5c542")
        for index, value in enumerate(self.blocks):
            label = "" if value is None else str(value + 1)
            button = Gtk.Button(label=label); button.update_property([Gtk.AccessibleProperty.LABEL], ["Block %d" % (index + 1)]); button.connect("clicked", self._remove, index); self.grid.attach(button, index % 3, index // 3, 1, 1)
        remaining = sum(value is not None for value in self.blocks)
        self.status.set_text("Solved!" if not remaining else "%d blocks remain" % remaining)

    def _remove(self, _button, index):
        value = self.blocks[index]
        if value is None: return
        group = [i for i, candidate in enumerate(self.blocks) if candidate == value]
        if len(group) < 2: self.status.set_text("Choose a block with a matching group."); return
        for i in group: self.blocks[i] = None
        self._render()

    def _reset(self, _button):
        self.blocks = [0, 0, 1, 1, 2, 2, 0, 1, 2]; self._render()
