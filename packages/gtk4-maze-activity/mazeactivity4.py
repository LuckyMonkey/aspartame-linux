"""Native GTK4 Maze Activity."""

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class MazeActivity(SimpleActivity):
    MOVES = {"Up": (0, -1), "Down": (0, 1), "Left": (-1, 0), "Right": (1, 0)}

    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("Maze"); self.position = [0, 0]; self.goal = [3, 3]; self._build(); self._render()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        root.set_margin_top(28); root.set_margin_bottom(28); root.set_margin_start(32); root.set_margin_end(32)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Maze game"])
        title = Gtk.Label(label="Maze", xalign=0); title.add_css_class("title-1"); root.append(title)
        root.append(Gtk.Label(label="Use the arrows to reach the golden goal.", xalign=0))
        self.grid = Gtk.Grid(row_spacing=3, column_spacing=3); self.grid.set_halign(Gtk.Align.CENTER); root.append(self.grid)
        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        for name in self.MOVES:
            button = Gtk.Button(label=name); button.update_property([Gtk.AccessibleProperty.LABEL], ["Move %s" % name]); button.connect("clicked", self._move, name); controls.append(button)
        root.append(controls)
        self.status = Gtk.Label(xalign=0); self.status.add_css_class("dim-label"); root.append(self.status)
        reset = Gtk.Button(label="New maze"); reset.connect("clicked", self._reset); root.append(reset)
        self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"button { min-width: 72px; min-height: 40px; border-radius: 18px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _render(self):
        child = self.grid.get_first_child()
        while child is not None:
            nxt = child.get_next_sibling(); self.grid.remove(child); child = nxt
        for y in range(4):
            for x in range(4):
                label = "●" if [x, y] == self.position else ("★" if [x, y] == self.goal else "")
                button = Gtk.Button(label=label); button.update_property([Gtk.AccessibleProperty.LABEL], ["Cell %d %d" % (x + 1, y + 1)]); button.connect("clicked", self._cell, x, y); self.grid.attach(button, x, y, 1, 1)
        self.status.set_text("You reached the goal!" if self.position == self.goal else "Position: %d, %d" % (self.position[0] + 1, self.position[1] + 1))

    def _move(self, _button, direction):
        dx, dy = self.MOVES[direction]; self.position[0] = max(0, min(3, self.position[0] + dx)); self.position[1] = max(0, min(3, self.position[1] + dy)); self._render()

    def _cell(self, _button, x, y):
        self.position = [x, y]; self._render()

    def _reset(self, _button):
        self.position = [0, 0]; self._render()
