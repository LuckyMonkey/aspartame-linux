"""Small native GTK4 clock Activity for the modern Sugar Space."""

from datetime import datetime

import gi

gi.require_version("Gdk", "4.0")
gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, GLib, Gtk
from sugar4.activity import SimpleActivity


class ClockActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Clock")
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18,
                       halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Clock"])
        root.set_accessible_role(Gtk.AccessibleRole.GROUP)
        self.clock = Gtk.Label()
        self.clock.add_css_class("clock-time")
        self.clock.update_property([Gtk.AccessibleProperty.LABEL], ["Current time"])
        root.append(self.clock)
        self.date = Gtk.Label()
        self.date.add_css_class("clock-date")
        self.date.update_property([Gtk.AccessibleProperty.LABEL], ["Current date"])
        root.append(self.date)
        self.set_canvas(root)
        self._install_css()
        self._tick()
        GLib.timeout_add_seconds(1, self._tick)

    def _install_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(b".clock-time { font-size: 72px; font-weight: bold; } .clock-date { font-size: 20px; }")
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _tick(self):
        now = datetime.now()
        self.clock.set_text(now.strftime("%H:%M:%S"))
        self.date.set_text(now.strftime("%A, %B %d, %Y"))
        return GLib.SOURCE_CONTINUE

    def write_file(self, file_path):
        with open(file_path, "w", encoding="utf-8") as stream:
            stream.write(self.clock.get_text())
