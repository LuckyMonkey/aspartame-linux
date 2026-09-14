"""Small, offline GTK4 Diamond Fusion matching game.

Two equal neighbouring diamonds fuse into a diamond of the next level.  The
model is intentionally independent from the renderer so the activity remains
predictable in the Casilda surface and easy to exercise with pointer input.
"""

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class DiamondFusionActivity(SimpleActivity):
    ROWS = 6
    COLUMNS = 6
    START = (1, 1, 2, 1, 3, 1, 2, 1, 1, 2, 1, 3, 1, 2, 1, 1, 2, 1,
             3, 1, 1, 2, 1, 2, 1, 3, 1, 1, 2, 1, 2, 1, 1, 2, 1, 3)
    COLORS = {1: (0.25, 0.62, 0.86), 2: (0.98, 0.65, 0.16), 3: (0.70, 0.30, 0.86),
              4: (0.30, 0.78, 0.47), 5: (0.95, 0.30, 0.35)}

    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Diamond Fusion")
        self._reset_model()
        self._build()

    def _reset_model(self):
        self.cells = list(self.START)
        self.selected = None
        self.score = 0

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        root.set_margin_top(24); root.set_margin_bottom(24)
        root.set_margin_start(30); root.set_margin_end(30)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Diamond Fusion puzzle"])
        title = Gtk.Label(label="Diamond Fusion", xalign=0)
        title.add_css_class("title-1"); root.append(title)
        self.status = Gtk.Label(label="Select two matching neighbouring diamonds to fuse.", xalign=0)
        self.status.update_property([Gtk.AccessibleProperty.LABEL], ["Game status"]); root.append(self.status)
        self.canvas = Gtk.DrawingArea()
        self.canvas.set_content_width(600); self.canvas.set_content_height(480)
        self.canvas.set_hexpand(True); self.canvas.set_vexpand(True); self.canvas.set_focusable(True)
        self.canvas.update_property([Gtk.AccessibleProperty.LABEL, Gtk.AccessibleProperty.DESCRIPTION],
                                    ["Diamond Fusion board", "Click two equal neighbouring diamonds to merge them"])
        self.canvas.set_draw_func(self._draw)
        click = Gtk.GestureClick(); click.connect("pressed", self._pressed); self.canvas.add_controller(click)
        root.append(self.canvas)
        reset = Gtk.Button(label="New game")
        reset.update_property([Gtk.AccessibleProperty.LABEL], ["Start a new Diamond Fusion game"])
        reset.connect("clicked", self._reset); root.append(reset)
        self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"button { min-height: 42px; border-radius: 19px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _cell_at(self, x, y):
        width = max(1, self.canvas.get_width()); height = max(1, self.canvas.get_height())
        size = min(width / self.COLUMNS, height / self.ROWS)
        left = (width - size * self.COLUMNS) / 2; top = (height - size * self.ROWS) / 2
        column = int((x - left) / size); row = int((y - top) / size)
        if 0 <= row < self.ROWS and 0 <= column < self.COLUMNS:
            return row * self.COLUMNS + column
        return None

    def _pressed(self, _gesture, _presses, x, y):
        index = self._cell_at(x, y)
        if index is None or not self.cells[index]: return
        if self.selected is None:
            self.selected = index; self.status.set_text("Choose a matching neighbour."); self.canvas.queue_draw(); return
        first, second = self.selected, index; self.selected = None
        adjacent = abs(first // self.COLUMNS - second // self.COLUMNS) + abs(first % self.COLUMNS - second % self.COLUMNS) == 1
        if adjacent and self.cells[first] == self.cells[second]:
            self.cells[first] = min(self.cells[first] + 1, max(self.COLORS)); self.cells[second] = 0
            self.score += 1; self.status.set_text(f"Fused! Score: {self.score}")
        else:
            self.status.set_text("Those diamonds do not match; select another pair.")
        self.canvas.queue_draw()

    def _reset(self, _button):
        self._reset_model(); self.status.set_text("Select two matching neighbouring diamonds to fuse."); self.canvas.queue_draw()

    def _draw(self, _area, cr, width, height):
        cr.set_source_rgb(0.97, 0.97, 0.97); cr.paint()
        size = min(width / self.COLUMNS, height / self.ROWS); left = (width - size * self.COLUMNS) / 2; top = (height - size * self.ROWS) / 2
        for index, level in enumerate(self.cells):
            row, column = divmod(index, self.COLUMNS); cx = left + (column + .5) * size; cy = top + (row + .5) * size
            cr.set_source_rgb(0.82, 0.86, 0.88); cr.rectangle(left + column * size + 2, top + row * size + 2, size - 4, size - 4); cr.fill()
            if not level: continue
            cr.set_source_rgb(*self.COLORS[level]); cr.move_to(cx, cy - size * .31); cr.line_to(cx + size * .31, cy); cr.line_to(cx, cy + size * .31); cr.line_to(cx - size * .31, cy); cr.close_path(); cr.fill()
            if index == self.selected:
                cr.set_source_rgb(0.05, 0.15, 0.25); cr.set_line_width(4); cr.move_to(cx, cy - size * .34); cr.line_to(cx + size * .34, cy); cr.line_to(cx, cy + size * .34); cr.line_to(cx - size * .34, cy); cr.close_path(); cr.stroke()
