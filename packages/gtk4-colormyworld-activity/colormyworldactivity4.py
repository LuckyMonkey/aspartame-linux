"""Native GTK4 Color My World Activity."""

import json
from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class ColorMyWorldActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("Color My World"); self._build()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12); root.set_margin_top(28); root.set_margin_bottom(28); root.set_margin_start(32); root.set_margin_end(32); root.update_property([Gtk.AccessibleProperty.LABEL], ["Color My World palette"])
        title = Gtk.Label(label="Color My World", xalign=0); title.add_css_class("title-1"); root.append(title)
        self.swatch = Gtk.DrawingArea(); self.swatch.set_content_height(220); self.swatch.set_vexpand(True); self.swatch.set_draw_func(self._draw); self.swatch.update_property([Gtk.AccessibleProperty.LABEL], ["Selected color swatch"]); root.append(self.swatch)
        self.name = Gtk.Label(label="Choose a color", xalign=0); root.append(self.name)
        colors = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        for label, color in (("Red", "#e33"), ("Gold", "#fc3"), ("Green", "#3c9"), ("Blue", "#39f"), ("Violet", "#c6f")):
            button = Gtk.Button(label=label); button.connect("clicked", self._choose, label, color); colors.append(button)
        root.append(colors); self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"button { min-height: 42px; border-radius: 19px; }"); display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _choose(self, _button, label, color): self.name.set_text(label); self._color_name = label; self._color = color; self.swatch.queue_draw()

    def _draw(self, _area, cr, width, height):
        color = getattr(self, "_color", "#ddd"); rgba = Gdk.RGBA(); rgba.parse(color); cr.set_source_rgba(rgba.red, rgba.green, rgba.blue, 1); cr.paint()

    def read_file(self, file_path):
        """Restore the selected palette color from a JSON Journal object."""
        colors = {"Red": "#e33", "Gold": "#fc3", "Green": "#3c9", "Blue": "#39f", "Violet": "#c6f"}
        try:
            payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
            name = payload.get("name", "") if isinstance(payload, dict) else ""
            if name not in colors:
                name = ""
        except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
            name = ""
        if name:
            self._choose(None, name, colors[name])
        else:
            self._color_name = ""; self._color = "#ddd"; self.name.set_text("Choose a color"); self.swatch.queue_draw()

    def write_file(self, file_path):
        """Save the selected palette color as a JSON Journal object."""
        Path(file_path).write_text(json.dumps({"name": getattr(self, "_color_name", "")}, sort_keys=True) + "\n", encoding="utf-8")
