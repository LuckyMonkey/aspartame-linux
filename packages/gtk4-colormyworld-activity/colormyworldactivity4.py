"""Native GTK4 Color My World Activity."""

import json
from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class ColorMyWorldActivity(SimpleActivity):
    PALETTE = (
        ("Red", "#e33"),
        ("Gold", "#fc3"),
        ("Green", "#3c9"),
        ("Blue", "#39f"),
        ("Violet", "#c6f"),
    )
    # A compact, dependency-free world silhouette.  The regions are kept
    # deliberately named and bounded so the activity remains useful offline
    # while a future artwork/data pass can replace the geometry without
    # changing the Journal contract.
    REGIONS = (
        ("Greenland", 0.28, 0.08, 0.11, 0.14),
        ("North America", 0.08, 0.21, 0.23, 0.24),
        ("South America", 0.25, 0.48, 0.13, 0.30),
        ("Europe", 0.45, 0.19, 0.12, 0.13),
        ("Africa", 0.45, 0.35, 0.16, 0.33),
        ("Asia", 0.57, 0.17, 0.25, 0.24),
        ("Southeast Asia", 0.67, 0.39, 0.15, 0.18),
        ("Australia", 0.77, 0.63, 0.15, 0.14),
    )
    REGION_LABELS = {
        "Southeast Asia": "SE Asia",
    }

    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Color My World")
        self._region_colors = {}
        self._selected_region = ""
        self._build()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12); root.set_margin_top(28); root.set_margin_bottom(28); root.set_margin_start(32); root.set_margin_end(32); root.set_hexpand(True); root.set_vexpand(True); root.update_property([Gtk.AccessibleProperty.LABEL], ["Color My World palette"])
        title = Gtk.Label(label="Color My World", xalign=0); title.add_css_class("title-1"); root.append(title)
        subtitle = Gtk.Label(label="Choose a color, then click a world region to fill it. Your map is saved in the Journal.", xalign=0); subtitle.add_css_class("dim-label"); subtitle.set_wrap(True); root.append(subtitle)
        self.swatch = Gtk.DrawingArea(); self.swatch.set_content_height(300); self.swatch.set_content_width(760); self.swatch.set_vexpand(True); self.swatch.set_hexpand(True); self.swatch.set_draw_func(self._draw); self.swatch.update_property([Gtk.AccessibleProperty.LABEL], ["World map coloring canvas"])
        map_click = Gtk.GestureClick(); map_click.connect("pressed", self._map_pressed); self.swatch.add_controller(map_click)
        swatch_frame = Gtk.Frame(label="World map"); swatch_frame.set_hexpand(True); swatch_frame.set_vexpand(True); swatch_frame.set_child(self.swatch); root.append(swatch_frame)
        self.name = Gtk.Label(label="No color selected yet", xalign=0); self.name.set_halign(Gtk.Align.CENTER); self.name.add_css_class("heading"); self.name.update_property([Gtk.AccessibleProperty.LABEL], ["Color selection status"]); root.append(self.name)
        colors = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        colors.set_halign(Gtk.Align.CENTER)
        self._palette_buttons = {}
        for label, color in self.PALETTE:
            button = Gtk.ToggleButton(label=label)
            button.set_tooltip_text(f"Choose {label}")
            button.update_property([Gtk.AccessibleProperty.LABEL, Gtk.AccessibleProperty.DESCRIPTION], [f"Choose {label}", f"Fill the preview with {label}"])
            button.connect("toggled", self._palette_toggled, label, color)
            self._palette_buttons[label] = button
            colors.append(button)
        palette_frame = Gtk.Frame(label="Palette"); palette_frame.set_halign(Gtk.Align.CENTER); palette_frame.set_child(colors)
        root.append(palette_frame)
        clear = Gtk.Button(label="Clear map")
        clear.set_halign(Gtk.Align.CENTER)
        clear.set_tooltip_text("Remove all colors from the world map")
        clear.update_property([Gtk.AccessibleProperty.LABEL], ["Clear world map"])
        clear.connect("clicked", self._clear_map)
        root.append(clear)
        self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"frame { padding: 8px; } drawingarea { background: #f4f7f8; border-radius: 12px; } button { min-height: 42px; min-width: 78px; border-radius: 19px; } togglebutton:checked { font-weight: bold; outline: 3px solid #2f88bd; outline-offset: 2px; }"); display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _palette_toggled(self, button, label, color):
        if not button.get_active():
            return
        for other_label, other in self._palette_buttons.items():
            if other_label != label and other.get_active():
                other.set_active(False)
        self._choose(label, color)

    def _choose(self, label, color):
        self.name.set_text(f"Selected color: {label}")
        self._color_name = label
        self._color = color
        self.swatch.queue_draw()

    def _draw(self, _area, cr, width, height):
        cr.set_source_rgb(0.96, 0.97, 0.98); cr.paint()
        for name, x, y, region_width, region_height in self.REGIONS:
            color = self._region_colors.get(name, "#d9e4e8")
            rgba = Gdk.RGBA(); rgba.parse(color)
            left = x * width; top = y * height
            cr.rectangle(left, top, region_width * width, region_height * height)
            cr.set_source_rgba(rgba.red, rgba.green, rgba.blue, 1); cr.fill_preserve()
            cr.set_source_rgb(0.32, 0.40, 0.43); cr.set_line_width(2); cr.stroke()
            label = self.REGION_LABELS.get(name, name)
            cr.set_source_rgb(0.22, 0.28, 0.30)
            cr.select_font_face("Sans", 0, 0)
            cr.set_font_size(max(10, min(16, width / 120)))
            extents = cr.text_extents(label)
            label_x = left + max(5, (region_width * width - extents.width) / 2)
            label_y = top + max(extents.height + 4, region_height * height / 2)
            cr.move_to(label_x, label_y)
            cr.show_text(label)
            if name == self._selected_region:
                cr.rectangle(left + 2, top + 2, region_width * width - 4, region_height * height - 4)
                cr.set_source_rgb(0.12, 0.35, 0.48); cr.set_line_width(4); cr.stroke()
        if not self._region_colors:
            cr.set_source_rgb(0.22, 0.28, 0.30); cr.select_font_face("Sans", 0, 0); cr.set_font_size(22)
            text = "Choose a color, then click a region"; extents = cr.text_extents(text)
            cr.move_to((width - extents.width) / 2 - extents.x_bearing, height * 0.92); cr.show_text(text)

    def _map_pressed(self, _gesture, _n_press, x, y):
        for name, region_x, region_y, region_width, region_height in self.REGIONS:
            if region_x * self.swatch.get_width() <= x <= (region_x + region_width) * self.swatch.get_width() and region_y * self.swatch.get_height() <= y <= (region_y + region_height) * self.swatch.get_height():
                if not getattr(self, "_color_name", ""):
                    self.name.set_text("Choose a color before selecting a region")
                    return
                self._selected_region = name
                self._region_colors[name] = self._color
                self.name.set_text(f"{name} · {self._color_name}")
                self.swatch.queue_draw()
                return

    def _clear_map(self, _button):
        self._region_colors.clear()
        self._selected_region = ""
        self.name.set_text(f"Selected color: {getattr(self, '_color_name', 'none')}")
        self.swatch.queue_draw()

    def read_file(self, file_path):
        """Restore the selected palette color from a JSON Journal object."""
        colors = dict(self.PALETTE)
        try:
            payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
            name = payload.get("name", "") if isinstance(payload, dict) else ""
            if name not in colors:
                name = ""
            saved_regions = payload.get("regions", {}) if isinstance(payload, dict) else {}
            region_names = {region[0] for region in self.REGIONS}
            self._region_colors = {
                region: value for region, value in saved_regions.items()
                if region in region_names and value in colors.values()
            } if isinstance(saved_regions, dict) else {}
        except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
            name = ""; self._region_colors = {}
        self._selected_region = ""
        if name:
            self._palette_buttons[name].set_active(True)
        else:
            for button in self._palette_buttons.values():
                button.set_active(False)
            self._color_name = ""; self._color = "#ddd"; self.name.set_text("No color selected yet"); self.swatch.queue_draw()
        if self._region_colors:
            self.name.set_text(f"{len(self._region_colors)} region(s) restored · {name or 'choose a color'}")
        self.swatch.queue_draw()

    def write_file(self, file_path):
        """Save the selected palette color as a JSON Journal object."""
        Path(file_path).write_text(json.dumps({"name": getattr(self, "_color_name", ""), "regions": self._region_colors}, sort_keys=True) + "\n", encoding="utf-8")
