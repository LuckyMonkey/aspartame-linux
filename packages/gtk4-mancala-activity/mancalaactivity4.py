"""GTK4-native two-row Mancala board."""

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class MancalaActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Mancala")
        self.pits = [4] * 12
        self.stores = [0, 0]
        self.turn = 0
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        root.set_margin_top(28); root.set_margin_bottom(28); root.set_margin_start(32); root.set_margin_end(32)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Mancala"]); root.set_accessible_role(Gtk.AccessibleRole.GROUP)
        title = Gtk.Label(label="Mancala", xalign=0); title.add_css_class("title-1"); root.append(title)
        self.status = Gtk.Label(label="Player 1: choose a pit.", xalign=0); root.append(self.status)
        board = Gtk.Grid(column_spacing=8, row_spacing=8); board.set_halign(Gtk.Align.CENTER); root.append(board)
        self.store_labels = []
        for store in range(2):
            label = Gtk.Label(label="0", width_chars=4); label.add_css_class("store"); self.store_labels.append(label)
            board.attach(label, 0 if store == 0 else 7, 0, 1, 2)
        self.buttons = []
        for index in range(6):
            for row, pit in ((0, index), (1, 11 - index)):
                button = Gtk.Button(label="4"); button.set_size_request(70, 54); button.connect("clicked", self._move, pit)
                button.update_property([Gtk.AccessibleProperty.LABEL], ["Pit %d" % (pit + 1)]); board.attach(button, index + 1, row, 1, 1); self.buttons.append((pit, button))
        reset = Gtk.Button(label="New game"); reset.connect("clicked", self._reset); root.append(reset)
        self.set_canvas(root); self._install_css()

    def _install_css(self):
        provider = Gtk.CssProvider(); provider.load_from_data(b".store { background: #d39b62; border-radius: 22px; padding: 18px; font-size: 24px; } button { min-height: 38px; border-radius: 18px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _move(self, _button, pit):
        if (self.turn == 0 and pit >= 6) or (self.turn == 1 and pit < 6) or not self.pits[pit]:
            self.status.set_text("Choose a non-empty pit on your side."); return
        stones = self.pits[pit]; self.pits[pit] = 0; pos = pit
        while stones:
            pos = (pos + 1) % 14
            if pos == 6 and self.turn == 1 or pos == 13 and self.turn == 0: continue
            if pos == 6: self.stores[0] += 1
            elif pos == 13: self.stores[1] += 1
            else: self.pits[self._pit_index(pos)] += 1
            stones -= 1
        self.turn = 1 - self.turn; self.status.set_text("Player %d: choose a pit." % (self.turn + 1)); self._render()

    @staticmethod
    def _pit_index(board_position):
        """Map the circular board positions 0..5 and 7..12 to pit storage."""
        return board_position if board_position < 6 else 18 - board_position

    def _render(self):
        for pit, button in self.buttons: button.set_label(str(self.pits[pit])); button.set_sensitive((self.turn == 0 and pit < 6) or (self.turn == 1 and pit >= 6))
        for index, label in enumerate(self.store_labels): label.set_text(str(self.stores[index]))

    def _reset(self, _button):
        self.pits = [4] * 12; self.stores = [0, 0]; self.turn = 0; self.status.set_text("Player 1: choose a pit."); self._render()
