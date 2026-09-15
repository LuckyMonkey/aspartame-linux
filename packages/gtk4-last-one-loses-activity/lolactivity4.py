"""Native GTK4 Last One Loses take-away game."""

import json
from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class LastOneLosesActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("Last One Loses"); self._reset()

    def _reset(self):
        self.pile = 15; self._build()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        root.set_margin_top(30); root.set_margin_bottom(30); root.set_margin_start(32); root.set_margin_end(32)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Last One Loses game"])
        title = Gtk.Label(label="Last One Loses", xalign=0); title.add_css_class("title-1"); root.append(title)
        self.status = Gtk.Label(label=f"{self.pile} tokens remain. Take 1–3; whoever takes the last loses.", xalign=0, wrap=True); root.append(self.status)
        self.pile_label = Gtk.Label(label="● " * self.pile, wrap=True); self.pile_label.add_css_class("title-2"); root.append(self.pile_label)
        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        for amount in (1, 2, 3):
            button = Gtk.Button(label=f"Take {amount}"); button.connect("clicked", self._take, amount); controls.append(button)
        root.append(controls)
        reset = Gtk.Button(label="New game"); reset.connect("clicked", lambda _b: self._reset()); root.append(reset)
        self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"button { min-height: 42px; border-radius: 19px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _take(self, _button, amount):
        if self.pile == 0: return
        self.pile = max(0, self.pile - amount); self.pile_label.set_text("● " * self.pile)
        self.status.set_text("You took the last token — you lose!" if self.pile == 0 else f"{self.pile} tokens remain.")

    def read_file(self, file_path):
        try:
            payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                self.pile = max(0, min(15, int(payload.get("pile", 15))))
                self._build()
        except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
            return

    def write_file(self, file_path):
        Path(file_path).write_text(json.dumps({"pile": self.pile}, sort_keys=True) + "\n", encoding="utf-8")
