"""Native GTK4 Stopwatch Activity with Journal resume support."""

import json
from pathlib import Path

from gi.repository import Gdk, GLib, Gtk
from sugar4.activity import SimpleActivity


class StopwatchActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("Stopwatch"); self.elapsed = 0; self.running = False; self._timer = None; self._build()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        root.set_margin_top(32); root.set_margin_bottom(32); root.set_margin_start(32); root.set_margin_end(32)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Stopwatch"])
        title = Gtk.Label(label="Stopwatch", xalign=0); title.add_css_class("title-1"); root.append(title)
        self.display = Gtk.Label(label="00:00.0"); self.display.add_css_class("title-1"); self.display.update_property([Gtk.AccessibleProperty.LABEL], ["Elapsed time"]); root.append(self.display)
        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.toggle = Gtk.Button(label="Start"); self.toggle.connect("clicked", self._toggle); controls.append(self.toggle)
        reset = Gtk.Button(label="Reset"); reset.connect("clicked", self._reset); controls.append(reset); root.append(controls)
        self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"button { min-height: 44px; border-radius: 19px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _toggle(self, _button):
        self.running = not self.running; self.toggle.set_label("Pause" if self.running else "Start")
        if self.running and self._timer is None: self._timer = GLib.timeout_add(100, self._tick)

    def _tick(self):
        if not self.running: self._timer = None; return GLib.SOURCE_REMOVE
        self.elapsed += 1; self._update_display(); return GLib.SOURCE_CONTINUE

    def _reset(self, _button):
        self.running = False; self.toggle.set_label("Start"); self.elapsed = 0; self._update_display()

    def _update_display(self):
        self.display.set_text(f"{self.elapsed // 600}:{(self.elapsed // 10) % 60:02d}.{self.elapsed % 10}")

    def read_file(self, file_path):
        """Restore elapsed time from a Journal object without restarting it."""
        try:
            state = json.loads(Path(file_path).read_text(encoding="utf-8"))
            self.elapsed = max(0, int(state.get("elapsed", 0)))
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            self.elapsed = 0
        self.running = False
        self.toggle.set_label("Start")
        self._update_display()

    def write_file(self, file_path):
        """Save elapsed time as a small, forward-compatible Journal object."""
        Path(file_path).write_text(
            json.dumps({"elapsed": self.elapsed}, sort_keys=True) + "\n",
            encoding="utf-8",
        )
