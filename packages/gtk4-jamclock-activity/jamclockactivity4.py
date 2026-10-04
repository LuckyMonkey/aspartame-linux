"""Native GTK4 JAMClock replacement for the modern Sugar Space.

The legacy Activity combined an analog clock, a calendar, and a configurable
alarm. Keep those useful learning workflows in native GTK4 widgets rather
than presenting a time label as a placeholder.
"""

import json
import math
from datetime import datetime
from pathlib import Path

import gi

gi.require_version("Gdk", "4.0")
gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, GLib, Gtk
from sugar4.activity import SimpleActivity


class JamClockFace(Gtk.DrawingArea):
    """A scalable analog face with a clear, child-friendly visual hierarchy."""

    def __init__(self):
        super().__init__()
        self.now = datetime.now()
        self.set_content_width(320)
        self.set_content_height(320)
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.set_draw_func(self._draw)
        self.update_property([Gtk.AccessibleProperty.LABEL], ["JAMClock face"])

    def update(self, now):
        self.now = now
        self.queue_draw()

    def _draw(self, _area, cr, width, height):
        size = min(width, height)
        cx, cy, radius = width / 2, height / 2, size * 0.39
        cr.set_source_rgb(0.98, 0.98, 0.96)
        cr.paint()

        cr.set_line_width(max(3, size * 0.014))
        cr.set_source_rgb(0.18, 0.53, 0.74)
        cr.arc(cx, cy, radius, 0, math.tau)
        cr.stroke()

        for mark in range(60):
            angle = mark * math.tau / 60 - math.pi / 2
            outer = radius * 0.94
            inner = radius * (0.85 if mark % 5 == 0 else 0.91)
            cr.set_line_width(max(2, size * (0.012 if mark % 5 == 0 else 0.006)))
            cr.move_to(cx + math.cos(angle) * inner, cy + math.sin(angle) * inner)
            cr.line_to(cx + math.cos(angle) * outer, cy + math.sin(angle) * outer)
            cr.stroke()

        cr.set_source_rgb(0.10, 0.20, 0.28)
        cr.select_font_face("Sans", 0, 1)
        cr.set_font_size(max(14, size * 0.055))
        for number in range(1, 13):
            angle = number * math.tau / 12 - math.pi / 2
            text = str(number)
            extents = cr.text_extents(text)
            cr.move_to(cx + math.cos(angle) * radius * 0.75 - extents.width / 2,
                       cy + math.sin(angle) * radius * 0.75 + extents.height / 2)
            cr.show_text(text)

        seconds = self.now.second
        hands = (
            (self.now.hour % 12 * 60 + self.now.minute, 720, radius * 0.52, 5, (0.00, 0.37, 0.89)),
            (self.now.minute * 60 + seconds, 3600, radius * 0.76, 4, (0.00, 0.60, 0.12)),
            (seconds, 60, radius * 0.84, 2, (0.90, 0.05, 0.04)),
        )
        for value, scale, length, line_width, color in hands:
            angle = value * math.tau / scale - math.pi / 2
            cr.set_source_rgb(*color)
            cr.set_line_width(max(line_width, size * 0.008))
            cr.move_to(cx, cy)
            cr.line_to(cx + math.cos(angle) * length, cy + math.sin(angle) * length)
            cr.stroke()
        cr.set_source_rgb(0.10, 0.20, 0.28)
        cr.arc(cx, cy, max(4, size * 0.018), 0, math.tau)
        cr.fill()


class JAMClockActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("JAMClock")
        self.alarm_hour = 12
        self.alarm_minute = 0
        self.alarm_enabled = False
        self._alarm_fired = None
        self._build()
        self._tick()
        GLib.timeout_add_seconds(1, self._tick)

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        for side in ("top", "bottom", "start", "end"):
            getattr(root, f"set_margin_{side}")(24)
        root.set_hexpand(True)
        root.set_vexpand(True)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["JAMClock"])
        root.set_accessible_role(Gtk.AccessibleRole.GROUP)

        title = Gtk.Label(label="JAMClock", xalign=0)
        title.add_css_class("title-2")
        root.append(title)

        content = Gtk.FlowBox()
        content.set_selection_mode(Gtk.SelectionMode.NONE)
        content.set_homogeneous(True)
        content.set_column_spacing(16)
        content.set_row_spacing(16)
        content.set_min_children_per_line(1)
        content.set_max_children_per_line(2)
        content.set_hexpand(True)
        content.set_vexpand(True)

        clock_card = Gtk.Frame(label="Clock")
        clock_card.set_hexpand(True)
        clock_card.set_vexpand(True)
        clock_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        for side in ("top", "bottom", "start", "end"):
            getattr(clock_panel, f"set_margin_{side}")(16)
        self.face = JamClockFace()
        clock_panel.append(self.face)
        self.time = Gtk.Label()
        self.time.add_css_class("jamclock-time")
        self.time.update_property([Gtk.AccessibleProperty.LABEL], ["Current time"])
        clock_panel.append(self.time)
        self.date = Gtk.Label()
        self.date.add_css_class("jamclock-date")
        self.date.update_property([Gtk.AccessibleProperty.LABEL], ["Current date"])
        clock_panel.append(self.date)
        clock_card.set_child(clock_panel)
        content.insert(clock_card, -1)

        side_card = Gtk.Frame(label="Calendar and alarm")
        side_card.set_hexpand(True)
        side_card.set_vexpand(True)
        side_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        for side in ("top", "bottom", "start", "end"):
            getattr(side_panel, f"set_margin_{side}")(16)

        self.calendar = Gtk.Calendar()
        self.calendar.set_hexpand(True)
        self.calendar.set_vexpand(True)
        self.calendar.update_property([Gtk.AccessibleProperty.LABEL], ["Calendar"])
        side_panel.append(self.calendar)

        alarm_heading = Gtk.Label(label="Alarm", xalign=0)
        alarm_heading.add_css_class("heading")
        side_panel.append(alarm_heading)
        alarm_controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        alarm_controls.set_halign(Gtk.Align.CENTER)
        self.hour = Gtk.SpinButton.new_with_range(0, 23, 1)
        self.hour.set_numeric(True)
        self.hour.set_wrap(True)
        self.hour.set_width_chars(2)
        self.hour.update_property([Gtk.AccessibleProperty.LABEL], ["Alarm hour"])
        self.hour.connect("value-changed", self._alarm_value_changed)
        alarm_controls.append(self.hour)
        separator = Gtk.Label(label=":")
        alarm_controls.append(separator)
        self.minute = Gtk.SpinButton.new_with_range(0, 59, 1)
        self.minute.set_numeric(True)
        self.minute.set_wrap(True)
        self.minute.set_width_chars(2)
        self.minute.update_property([Gtk.AccessibleProperty.LABEL], ["Alarm minute"])
        self.minute.connect("value-changed", self._alarm_value_changed)
        alarm_controls.append(self.minute)
        side_panel.append(alarm_controls)

        self.alarm_button = Gtk.ToggleButton(label="Alarm off")
        self.alarm_button.set_hexpand(True)
        self.alarm_button.set_tooltip_text("Enable or disable the alarm")
        self.alarm_button.update_property([Gtk.AccessibleProperty.LABEL], ["Alarm on or off"])
        self.alarm_button.connect("toggled", self._alarm_toggled)
        side_panel.append(self.alarm_button)
        self.alarm_status = Gtk.Label(label="Set a time, then enable the alarm", wrap=True)
        self.alarm_status.update_property([Gtk.AccessibleProperty.LABEL], ["Alarm status"])
        side_panel.append(self.alarm_status)
        side_card.set_child(side_panel)
        content.insert(side_card, -1)
        root.append(content)

        self.set_canvas(root)
        provider = Gtk.CssProvider()
        provider.load_from_data(
            b".jamclock-time { font-size: 42px; font-weight: bold; } "
            b".jamclock-date { font-size: 18px; } button { min-height: 42px; }"
        )
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    def _tick(self):
        now = datetime.now()
        self.face.update(now)
        self.time.set_text(now.strftime("%H:%M:%S"))
        self.date.set_text(now.strftime("%A, %B %d, %Y"))
        alarm_key = (now.date(), now.hour, now.minute)
        if self.alarm_enabled and (now.hour, now.minute) == (self.alarm_hour, self.alarm_minute):
            if self._alarm_fired != alarm_key:
                self._alarm_fired = alarm_key
                self.alarm_status.set_text("Alarm ringing")
                display = Gdk.Display.get_default()
                if display:
                    display.beep()
        elif self.alarm_enabled and self._alarm_fired != alarm_key:
            self.alarm_status.set_text(
                f"Alarm set for {self.alarm_hour:02d}:{self.alarm_minute:02d}"
            )
        return GLib.SOURCE_CONTINUE

    def _alarm_value_changed(self, _spin):
        self.alarm_hour = int(self.hour.get_value())
        self.alarm_minute = int(self.minute.get_value())
        self._alarm_fired = None
        if self.alarm_enabled:
            self.alarm_status.set_text(
                f"Alarm set for {self.alarm_hour:02d}:{self.alarm_minute:02d}"
            )

    def _alarm_toggled(self, button):
        self.alarm_enabled = button.get_active()
        button.set_label("Alarm on" if self.alarm_enabled else "Alarm off")
        self._alarm_fired = None
        if self.alarm_enabled:
            self.alarm_status.set_text(
                f"Alarm set for {self.alarm_hour:02d}:{self.alarm_minute:02d}"
            )
        else:
            self.alarm_status.set_text("Set a time, then enable the alarm")

    def read_file(self, file_path):
        """Restore alarm settings from a Journal object safely."""
        try:
            state = json.loads(Path(file_path).read_text(encoding="utf-8"))
            if not isinstance(state, dict):
                raise ValueError("state must be an object")
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            state = {}
        try:
            self.alarm_hour = min(23, max(0, int(state.get("alarm_hour", 12))))
            self.alarm_minute = min(59, max(0, int(state.get("alarm_minute", 0))))
        except (TypeError, ValueError):
            self.alarm_hour, self.alarm_minute = 12, 0
        self.alarm_enabled = bool(state.get("alarm_enabled", False))
        self.hour.set_value(self.alarm_hour)
        self.minute.set_value(self.alarm_minute)
        self.alarm_button.set_active(self.alarm_enabled)
        self._alarm_toggled(self.alarm_button)

    def write_file(self, file_path):
        Path(file_path).write_text(
            json.dumps({
                "alarm_enabled": self.alarm_enabled,
                "alarm_hour": self.alarm_hour,
                "alarm_minute": self.alarm_minute,
            }, sort_keys=True) + "\n",
            encoding="utf-8",
        )
