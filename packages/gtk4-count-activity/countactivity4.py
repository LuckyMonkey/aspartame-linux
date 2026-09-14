"""GTK4-native layered counting Activity.

The model stays deliberately small: every layer is an XY boolean plane.  The
GTK4 renderer draws the selected plane strongly and its neighbours as
translucent context, so layer traversal remains visible without a second
window or a GTK3 compatibility import.
"""

import json

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class CountActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Count")
        self.width, self.height = 5, 4
        self.layers = [self._empty_layer()]
        self.current_layer = 0
        self._press_cell = None
        self._drag_origin = (0, 0)
        self._paint_add = True

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Count"])
        root.set_accessible_role(Gtk.AccessibleRole.GROUP)
        root.set_margin_start(28)
        root.set_margin_end(28)
        root.set_margin_top(22)
        root.set_margin_bottom(22)
        title = Gtk.Label(label="Count", xalign=0)
        title.add_css_class("title-1")
        root.append(title)
        self.total = Gtk.Label(xalign=0)
        self.total.add_css_class("count-total")
        root.append(self.total)

        content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=18)
        content.set_hexpand(True)
        content.set_vexpand(True)
        self.canvas = Gtk.DrawingArea()
        self.canvas.set_size_request(760, 520)
        self.canvas.set_content_width(760)
        self.canvas.set_content_height(520)
        self.canvas.add_css_class("count-canvas")
        self.canvas.set_hexpand(True)
        self.canvas.set_vexpand(True)
        self.canvas.set_visible(True)
        self.canvas.set_draw_func(self._draw)
        canvas_box = Gtk.Box()
        canvas_box.set_size_request(760, 520)
        canvas_box.set_hexpand(False)
        canvas_box.set_vexpand(True)
        canvas_box.set_visible(True)
        overlay = Gtk.Overlay()
        self.overlay = overlay
        overlay.set_hexpand(True)
        overlay.set_vexpand(True)
        overlay.set_child(self.canvas)
        self.grid = Gtk.Grid(column_spacing=3, row_spacing=3)
        self.grid.add_css_class("count-grid")
        self.grid.set_halign(Gtk.Align.CENTER)
        self.grid.set_valign(Gtk.Align.CENTER)
        overlay.add_overlay(self.grid)
        self._cells = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                button = Gtk.Button()
                button.set_size_request(82, 82)
                button.connect("clicked", self._cell_clicked, x, y)
                row.append(button)
                self.grid.attach(button, x, y, 1, 1)
            self._cells.append(row)
        grid_drag = Gtk.GestureDrag()
        grid_drag.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        grid_drag.connect("drag-begin", self._grid_drag_begin)
        grid_drag.connect("drag-update", self._grid_drag_update)
        grid_drag.connect("drag-end", self._grid_drag_end)
        self.grid.add_controller(grid_drag)
        self._context_grids = []
        canvas_box.append(overlay)
        content.append(canvas_box)

        rail = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        rail.set_size_request(190, -1)
        rail.set_hexpand(False)
        rail.set_valign(Gtk.Align.CENTER)
        heading = Gtk.Label(label="EDIT LAYER", xalign=0)
        heading.add_css_class("dim-label")
        rail.append(heading)
        self.layer_label = Gtk.Label(xalign=0)
        self.layer_label.add_css_class("count-layer")
        rail.append(self.layer_label)
        self.layer_total = Gtk.Label(xalign=0)
        self.layer_total.add_css_class("dim-label")
        rail.append(self.layer_total)
        self._button(rail, "↑  Back layer", self._previous_layer)
        self._button(rail, "↓  Forward layer", self._next_layer)
        self._button(rail, "＋  New layer", self._add_layer)
        self._button(rail, "⧉  Copy layer", self._copy_layer)
        self._button(rail, "Delete layer", self._delete_layer)
        content.append(rail)
        root.append(content)
        self.set_canvas(root)
        self._install_css()
        self._render()

    @staticmethod
    def _empty_layer():
        return [[False] * 5 for _ in range(4)]

    def _button(self, parent, label, callback):
        button = Gtk.Button(label=label)
        button.set_hexpand(True)
        button.connect("clicked", callback)
        parent.append(button)

    def _install_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(b"""
            .count-total { font-size: 42px; font-weight: bold; color: #2f88bd; }
            .count-layer { font-size: 20px; font-weight: bold; color: #2f88bd; }
            .count-canvas { background-color: #f7f8f9; border: 1px solid #c5d1d8; }
            .count-grid button { background: #ffffff; border: 1px solid #6f8794; }
            .count-grid button.occupied { background: #6d767b; }
            button { min-height: 38px; border-radius: 18px; }
        """)
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _render(self):
        total = sum(sum(row) for layer in self.layers for row in layer)
        current = sum(sum(row) for row in self.layers[self.current_layer])
        self.total.set_text(str(total))
        self.layer_label.set_text(
            "Layer %d of %d" % (self.current_layer + 1, len(self.layers)))
        self.layer_total.set_text("%d on this layer" % current)
        for y, row in enumerate(self._cells):
            for x, button in enumerate(row):
                button.remove_css_class("occupied")
                if self.layers[self.current_layer][y][x]:
                    button.add_css_class("occupied")
                button.update_property(
                    [Gtk.AccessibleProperty.LABEL],
                    ["Cell %d, %d%s" % (x + 1, y + 1,
                     ", filled" if self.layers[self.current_layer][y][x]
                     else "")])
        self._refresh_context_grids()
        self.canvas.queue_draw()

    def _refresh_context_grids(self):
        for grid in self._context_grids:
            self.overlay.remove_overlay(grid)
        self._context_grids.clear()
        for index, layer in enumerate(self.layers):
            relative = index - self.current_layer
            if relative == 0:
                continue
            grid = Gtk.Grid(column_spacing=3, row_spacing=3)
            grid.set_halign(Gtk.Align.CENTER)
            grid.set_valign(Gtk.Align.CENTER)
            grid.set_opacity(.24 if relative > 0 else .16)
            grid.set_margin_start(relative * 18)
            grid.set_margin_top(relative * -12)
            for y, row in enumerate(layer):
                for x, occupied in enumerate(row):
                    button = Gtk.Button()
                    button.set_size_request(82, 82)
                    button.set_sensitive(False)
                    if occupied:
                        button.add_css_class("occupied")
                    grid.attach(button, x, y, 1, 1)
            self.overlay.add_overlay(grid)
            self._context_grids.append(grid)
        # Keep the selected plane above context grids.
        self.overlay.remove_overlay(self.grid)
        self.overlay.add_overlay(self.grid)

    def _cell_clicked(self, _button, x, y):
        self.layers[self.current_layer][y][x] = not self.layers[self.current_layer][y][x]
        self._render()

    def _grid_cell(self, x, y):
        column = int(x // 85)
        row = int(y // 85)
        if 0 <= column < self.width and 0 <= row < self.height:
            return column, row
        return None

    def _grid_drag_begin(self, _gesture, x, y):
        self._drag_origin = (x, y)
        self._press_cell = self._grid_cell(x, y)
        if self._press_cell:
            px, py = self._press_cell
            self._paint_add = not self.layers[self.current_layer][py][px]
            self._paint_rectangle(self._press_cell)

    def _grid_drag_update(self, _gesture, offset_x, offset_y):
        if self._press_cell is None:
            return
        origin_x, origin_y = self._drag_origin
        self._paint_rectangle(self._grid_cell(origin_x + offset_x,
                                               origin_y + offset_y))

    def _grid_drag_end(self, *_args):
        self._press_cell = None

    def _paint_rectangle(self, end_cell):
        if self._press_cell is None or end_cell is None:
            return
        x0, y0 = self._press_cell
        x1, y1 = end_cell
        for row in range(min(y0, y1), max(y0, y1) + 1):
            for column in range(min(x0, x1), max(x0, x1) + 1):
                self.layers[self.current_layer][row][column] = self._paint_add
        self._render()

    def _geometry(self):
        width = max(1, self.canvas.get_width())
        height = max(1, self.canvas.get_height())
        size = min(92, (width - 44) / self.width, (height - 44) / self.height)
        size = max(28, size)
        depth_x, depth_y = size * .28, -size * .18
        span = len(self.layers) - 1
        total_w = self.width * size + span * abs(depth_x)
        total_h = self.height * size + span * abs(depth_y)
        ox = (width - total_w) / 2 + max(0, -span * depth_x)
        oy = (height - total_h) / 2 + max(0, -span * depth_y)
        return ox, oy, size, depth_x, depth_y

    def _draw(self, _area, cr, _width, _height):
        cr.set_source_rgb(.97, .98, .99)
        cr.paint()
        ox, oy, size, dx, dy = self._geometry()
        order = [i for i in range(len(self.layers) - 1, -1, -1)]
        for index in order:
            relative = index - self.current_layer
            selected = relative == 0
            alpha = 1.0 if selected else (.34 if relative > 0 else .20)
            px, py = relative * dx, relative * dy
            cr.set_source_rgba(.13, .42, .64, .95 if selected else .45)
            cr.set_line_width(2 if selected else 1)
            for x in range(self.width + 1):
                cr.move_to(ox + px + x * size, oy + py)
                cr.line_to(ox + px + x * size, oy + py + self.height * size)
            for y in range(self.height + 1):
                cr.move_to(ox + px, oy + py + y * size)
                cr.line_to(ox + px + self.width * size, oy + py + y * size)
            cr.stroke()
            for y, row in enumerate(self.layers[index]):
                for x, occupied in enumerate(row):
                    if not occupied:
                        continue
                    left, top = ox + px + x * size, oy + py + y * size
                    cr.set_source_rgba(.40, .44, .46, alpha)
                    cr.rectangle(left + 1, top + 1, size - 3, size - 3)
                    cr.fill_preserve()
                    cr.set_source_rgba(.12, .15, .17, alpha)
                    cr.set_line_width(2 if selected else 1)
                    cr.stroke()
                    if selected:
                        cr.set_source_rgba(.67, .72, .75, alpha)
                        cr.move_to(left + 1, top + 1)
                        cr.line_to(left + 1 + dx, top + 1 + dy)
                        cr.line_to(left + size - 2 + dx, top + 1 + dy)
                        cr.line_to(left + size - 2, top + 1)
                        cr.close_path()
                        cr.fill()

    def _cell(self, x, y):
        ox, oy, size, _dx, _dy = self._geometry()
        cell = int((x - ox) // size), int((y - oy) // size)
        return cell if 0 <= cell[0] < self.width and 0 <= cell[1] < self.height else None

    def _paint(self, cell):
        if cell is None:
            return
        x, y = cell
        self.layers[self.current_layer][y][x] = self._paint_add
        self._render()

    def _drag_begin(self, _gesture, x, y):
        self._drag_origin = (x, y)
        cell = self._cell(x, y)
        self._press_cell = cell
        if cell:
            px, py = cell
            self._paint_add = not self.layers[self.current_layer][py][px]
            self._paint(cell)

    def _drag_update(self, _gesture, offset_x, offset_y):
        if self._press_cell is None:
            return
        origin_x, origin_y = self._drag_origin
        cell = self._cell(origin_x + offset_x, origin_y + offset_y)
        if cell:
            x0, y0 = self._press_cell
            x1, y1 = cell
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for x in range(min(x0, x1), max(x0, x1) + 1):
                    self.layers[self.current_layer][y][x] = self._paint_add
            self._render()

    def _drag_end(self, *_args):
        self._press_cell = None

    def _add_layer(self, *_args):
        self.layers.insert(self.current_layer + 1, self._empty_layer())
        self._render()

    def _copy_layer(self, *_args):
        self.layers.insert(self.current_layer + 1,
                           json.loads(json.dumps(self.layers[self.current_layer])))
        self._render()

    def _delete_layer(self, *_args):
        if len(self.layers) > 1:
            self.layers.pop(self.current_layer)
            self.current_layer = min(self.current_layer, len(self.layers) - 1)
            self._render()

    def _previous_layer(self, *_args):
        self.current_layer = max(0, self.current_layer - 1)
        self._render()

    def _next_layer(self, *_args):
        self.current_layer = min(len(self.layers) - 1, self.current_layer + 1)
        self._render()

    def write_file(self, file_path):
        with open(file_path, "w", encoding="utf-8") as stream:
            json.dump({"layers": self.layers, "current_layer": self.current_layer}, stream)

    def read_file(self, file_path):
        with open(file_path, encoding="utf-8") as stream:
            state = json.load(stream)
        self.layers = state["layers"]
        self.current_layer = min(state.get("current_layer", 0), len(self.layers) - 1)
        self._render()
