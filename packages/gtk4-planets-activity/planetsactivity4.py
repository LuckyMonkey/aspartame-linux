"""Native GTK4 Planets orbit Activity."""

import json
import math
from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class PlanetsActivity(SimpleActivity):
    PLANETS = (
        ("Mercury", (0.62, 0.62, 0.62), "Small, rocky, and closest to the Sun."),
        ("Venus", (0.92, 0.62, 0.28), "A bright, cloud-covered world."),
        ("Earth", (0.20, 0.55, 0.95), "Our home planet, rich with water and life."),
        ("Mars", (0.88, 0.30, 0.18), "The red planet with towering volcanoes."),
        ("Jupiter", (0.78, 0.58, 0.38), "A giant world with a famous storm."),
    )

    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Planets")
        self.selected = "Earth"
        self._build()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        root.set_margin_top(24)
        root.set_margin_bottom(24)
        root.set_margin_start(30)
        root.set_margin_end(30)
        root.set_hexpand(True)
        root.set_vexpand(True)
        root.update_property(
            [Gtk.AccessibleProperty.LABEL], ["Planets orbit canvas"]
        )

        title = Gtk.Label(label="Planets", xalign=0)
        title.add_css_class("title-1")
        root.append(title)

        prompt = Gtk.Label(
            label="Explore the inner planets — choose a planet to highlight its orbit.",
            xalign=0,
        )
        prompt.add_css_class("dim-label")
        root.append(prompt)

        self._drawing_area = Gtk.DrawingArea()
        self._drawing_area.set_content_width(640)
        self._drawing_area.set_content_height(384)
        self._drawing_area.set_hexpand(True)
        self._drawing_area.set_vexpand(True)
        self._drawing_area.set_draw_func(self._draw)
        self._drawing_area.update_property(
            [Gtk.AccessibleProperty.LABEL], ["Solar system illustration"]
        )
        canvas_frame = Gtk.Frame(label="Solar system")
        canvas_frame.add_css_class("planets-surface")
        canvas_frame.set_hexpand(True)
        canvas_frame.set_vexpand(True)
        canvas_frame.set_child(self._drawing_area)
        root.append(canvas_frame)

        selection = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        self.info = Gtk.Label(xalign=0)
        self.info.add_css_class("heading")
        selection.append(self.info)
        self.details = Gtk.Label(xalign=0, wrap=True)
        self.details.add_css_class("dim-label")
        selection.append(self.details)
        selection_frame = Gtk.Frame(label="Selected planet")
        selection_frame.set_child(selection)
        root.append(selection_frame)

        buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        buttons.set_halign(Gtk.Align.CENTER)
        for name, _color, _description in self.PLANETS:
            button = Gtk.Button(label=name)
            button.update_property([Gtk.AccessibleProperty.LABEL], [f"Select {name}"])
            button.connect("clicked", self._select, name)
            buttons.append(button)
        root.append(buttons)
        self.set_canvas(root)
        self._update_selection()

        provider = Gtk.CssProvider()
        provider.load_from_data(
            b"frame.planets-surface { border: 2px solid #526b9a; "
            b"border-radius: 10px; padding: 8px; } "
            b"frame { padding: 8px; } button { min-height: 42px; "
            b"border-radius: 19px; }"
        )
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    def _update_selection(self):
        description = next(
            description
            for name, _color, description in self.PLANETS
            if name == self.selected
        )
        self.info.set_text(f"{self.selected} — selected planet")
        self.details.set_text(description)
        self._drawing_area.queue_draw()

    def _select(self, _button, name):
        self.selected = name
        self._update_selection()

    def read_file(self, file_path):
        """Restore the selected planet from a JSON Journal object."""
        try:
            payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
            selected = payload.get("selected", "Earth") if isinstance(payload, dict) else "Earth"
            if selected not in {name for name, _color, _description in self.PLANETS}:
                selected = "Earth"
        except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
            selected = "Earth"
        self._select(None, selected)

    def write_file(self, file_path):
        """Save the selected planet as a JSON Journal object."""
        Path(file_path).write_text(json.dumps({"selected": self.selected}, sort_keys=True) + "\n", encoding="utf-8")

    def _draw(self, _area, cr, width, height):
        cr.set_source_rgb(0.02, 0.04, 0.12)
        cr.paint()
        cx, cy = width / 2, height / 2
        scale = min(width / 1000, height / 600)

        # A small deterministic star field keeps the canvas legible without
        # requiring an image asset or making the Activity depend on the net.
        for star_x, star_y, star_size in (
            (0.08, 0.20, 1.2), (0.19, 0.72, 1.0), (0.31, 0.12, 0.9),
            (0.67, 0.18, 1.1), (0.83, 0.66, 1.0), (0.91, 0.31, 1.3),
        ):
            cr.set_source_rgb(0.72, 0.78, 0.94)
            cr.arc(width * star_x, height * star_y, star_size, 0, 2 * math.pi)
            cr.fill()

        sun_radius = max(12, 18 * scale)
        cr.set_source_rgb(1.0, 0.75, 0.10)
        cr.arc(cx, cy, sun_radius, 0, 2 * math.pi)
        cr.fill()

        for index, (name, color, _description) in enumerate(self.PLANETS):
            radius = (48 + index * 36) * scale
            cr.set_source_rgb(0.25, 0.30, 0.50)
            cr.set_line_width(max(1, scale))
            cr.arc(cx, cy, radius, 0, 2 * math.pi)
            cr.stroke()
            angle = index * 1.1
            px = cx + radius * math.cos(angle)
            py = cy + radius * math.sin(angle)
            planet_radius = (7 if name != "Jupiter" else 12) * scale
            cr.set_source_rgb(*color)
            cr.arc(px, py, planet_radius, 0, 2 * math.pi)
            cr.fill()
            if name == self.selected:
                cr.set_source_rgb(1.0, 1.0, 1.0)
                cr.set_line_width(max(2, 3 * scale))
                cr.arc(px, py, planet_radius + 7 * scale, 0, 2 * math.pi)
                cr.stroke()
                cr.set_source_rgb(0.92, 0.94, 1.0)
                cr.select_font_face("Sans", 0, 0)
                cr.set_font_size(max(12, 18 * scale))
                cr.move_to(px + 12 * scale, py - 12 * scale)
                cr.show_text(name)
