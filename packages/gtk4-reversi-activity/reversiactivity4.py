"""GTK4-native Reversi board with legal capture and flip moves."""

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class ReversiActivity(SimpleActivity):
    DIRECTIONS = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))

    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("Reversi"); self._reset_board()
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        root.set_margin_top(24); root.set_margin_bottom(24); root.set_margin_start(28); root.set_margin_end(28)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Reversi"]); root.set_accessible_role(Gtk.AccessibleRole.GROUP)
        title = Gtk.Label(label="Reversi", xalign=0); title.add_css_class("title-1"); root.append(title)
        self.status = Gtk.Label(xalign=0); root.append(self.status)
        self.grid = Gtk.Grid(column_spacing=3, row_spacing=3); self.grid.set_halign(Gtk.Align.CENTER); root.append(self.grid)
        self.cells = []
        for y in range(8):
            row = []
            for x in range(8):
                button = Gtk.Button(label=" "); button.set_size_request(52, 52); button.connect("clicked", self._play, x, y)
                button.update_property([Gtk.AccessibleProperty.LABEL], ["Square %d, %d" % (x + 1, y + 1)]); self.grid.attach(button, x, y, 1, 1); row.append(button)
            self.cells.append(row)
        reset = Gtk.Button(label="New game"); reset.connect("clicked", self._new_game); root.append(reset)
        self.set_canvas(root); self._install_css(); self._render()

    def _install_css(self):
        provider = Gtk.CssProvider(); provider.load_from_data(b".reversi-board { background: #438b5e; } button { min-height: 38px; border-radius: 18px; } button.black { background: #202124; color: white; border-radius: 26px; } button.white { background: #f4f4f4; color: #222; border-radius: 26px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _reset_board(self):
        self.board = [[0] * 8 for _ in range(8)]; self.board[3][3] = self.board[4][4] = 2; self.board[3][4] = self.board[4][3] = 1; self.player = 1

    def _moves(self, player):
        other = 3 - player; result = {}
        for y in range(8):
            for x in range(8):
                if self.board[y][x]: continue
                flips = []
                for dx, dy in self.DIRECTIONS:
                    xx, yy, line = x + dx, y + dy, []
                    while 0 <= xx < 8 and 0 <= yy < 8 and self.board[yy][xx] == other:
                        line.append((xx, yy)); xx += dx; yy += dy
                    if line and 0 <= xx < 8 and 0 <= yy < 8 and self.board[yy][xx] == player: flips.extend(line)
                if flips: result[(x, y)] = flips
        return result

    def _play(self, _button, x, y):
        moves = self._moves(self.player)
        if (x, y) not in moves: self.status.set_text("Choose a square that captures a line of discs."); return
        self.board[y][x] = self.player
        for xx, yy in moves[(x, y)]: self.board[yy][xx] = self.player
        self.player = 3 - self.player
        if not self._moves(self.player): self.player = 3 - self.player
        self._render()

    def _render(self):
        counts = [sum(cell == player for row in self.board for cell in row) for player in (1, 2)]
        moves = self._moves(self.player); self.status.set_text("Player %d · Black %d  White %d · %d legal move%s" % (self.player, counts[0], counts[1], len(moves), "" if len(moves) == 1 else "s"))
        if not moves and not self._moves(3 - self.player):
            winner = "Black" if counts[0] > counts[1] else "White" if counts[1] > counts[0] else "Nobody"
            self.status.set_text("Game over · %s wins (%d–%d). Start a new game to play again." % (winner, counts[0], counts[1]))
        for y, row in enumerate(self.cells):
            for x, button in enumerate(row):
                for css in ("black", "white"): button.remove_css_class(css)
                value = self.board[y][x]; button.set_label("●" if value else ("+" if (x, y) in moves else " "))
                if value == 1: button.add_css_class("black")
                elif value == 2: button.add_css_class("white")

    def _new_game(self, _button): self._reset_board(); self._render()
