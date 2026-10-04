"""Native GTK4 Clock Activity with responsive learning controls.

The GTK3 activity offered three ways to learn about time and a handful of
small display options. This port keeps those useful workflows in a compact
GTK4 surface instead of reducing the Activity to a pair of labels.
"""

import json
import math
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

import gi

gi.require_version("Gdk", "4.0")
gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, GLib, Gtk
from sugar4.activity import SimpleActivity


MODES = ("simple", "nice", "digital")
WORDS = (
    "midnight", "one", "two", "three", "four", "five", "six", "seven",
    "eight", "nine", "ten", "eleven", "twelve", "noon",
)
MINUTES = (
    "one", "two", "three", "four", "five", "six", "seven", "eight",
    "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
    "sixteen", "seventeen", "eighteen", "nineteen", "twenty", "twenty-one",
    "twenty-two", "twenty-three", "twenty-four", "twenty-five", "twenty-six",
    "twenty-seven", "twenty-eight", "twenty-nine", "thirty", "thirty-one",
    "thirty-two", "thirty-three", "thirty-four", "thirty-five", "thirty-six",
    "thirty-seven", "thirty-eight", "thirty-nine", "forty", "forty-one",
    "forty-two", "forty-three", "forty-four", "forty-five", "forty-six",
    "forty-seven", "forty-eight", "forty-nine", "fifty", "fifty-one",
    "fifty-two", "fifty-three", "fifty-four", "fifty-five", "fifty-six",
    "fifty-seven", "fifty-eight", "fifty-nine",
)


class ClockFace(Gtk.DrawingArea):
    """A small, scalable analog/digital clock drawing surface."""

    def __init__(self):
        super().__init__()
        self.mode = "simple"
        self.ticking = True
        self.interactive = False
        self.manual_time = False
        self.now = datetime.now()
        self.on_time_changed = None
        self.set_content_width(320)
        self.set_content_height(320)
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.set_draw_func(self._draw)
        self.update_property([Gtk.AccessibleProperty.LABEL], ["Clock face"])
        drag = Gtk.GestureDrag()
        drag.set_button(1)
        drag.connect("drag-begin", self._drag_begin)
        drag.connect("drag-update", self._drag_update)
        drag.connect("drag-end", self._drag_end)
        self.add_controller(drag)
        self._drag = drag
        self._hand = None

    def update(self, now, mode, ticking):
        self.now = now
        self.mode = mode
        self.ticking = ticking
        self.queue_draw()

    def set_interactive(self, enabled):
        self.interactive = bool(enabled)
        self._hand = None
        if not self.interactive:
            self.manual_time = False
            self.now = datetime.now()
        self.queue_draw()

    @staticmethod
    def _angle_and_distance(x, y, cx, cy):
        adjacent = x - cx
        opposite = cy - y
        return math.atan2(adjacent, opposite) % math.tau, math.hypot(adjacent, opposite)

    @staticmethod
    def _angle_distance(first, second):
        return abs((first - second + math.pi) % math.tau - math.pi)

    def _hand_angle(self, hand):
        seconds = self.now.second if self.ticking else 0
        if hand == "hour":
            return (self.now.hour % 12 * 60 + self.now.minute) * math.tau / 720
        if hand == "minute":
            return (self.now.minute * 60 + seconds) * math.tau / 3600
        return seconds * math.tau / 60

    def _drag_begin(self, _gesture, x, y):
        if not self.interactive or self.mode == "digital":
            return
        width = self.get_width()
        height = self.get_height()
        cx, cy = width / 2, height / 2
        angle, distance = self._angle_and_distance(x, y, cx, cy)
        size = min(width, height)
        radius = size * 0.38
        candidates = (
            ("hour", radius * 0.52),
            ("minute", radius * 0.76),
            ("second", radius * 0.84),
        )
        eligible = [
            (self._angle_distance(angle, self._hand_angle(hand)), hand)
            for hand, length in candidates
            if distance <= length + max(18, size * 0.05)
        ]
        if eligible:
            self._hand = min(eligible)[1]

    def _drag_update(self, gesture, offset_x, offset_y):
        if self._hand is None:
            return
        _ok, start_x, start_y = gesture.get_start_point()
        width = self.get_width()
        height = self.get_height()
        angle, _distance = self._angle_and_distance(
            start_x + offset_x, start_y + offset_y, width / 2, height / 2
        )
        if self._hand == "minute":
            minute = round(angle * 60 / math.tau) % 60
            self.now = self.now.replace(minute=minute, second=0)
        elif self._hand == "hour":
            hour = round(angle * 12 / math.tau) % 12
            hour = hour or 12
            hour24 = hour % 12 + (12 if self.now.hour >= 12 else 0)
            self.now = self.now.replace(hour=hour24, second=0)
        else:
            second = round(angle * 60 / math.tau) % 60
            self.now = self.now.replace(second=second)
        self.manual_time = True
        if self.on_time_changed:
            self.on_time_changed(self.now)
        self.queue_draw()

    def _drag_end(self, _gesture, _offset_x, _offset_y):
        self._hand = None

    def _draw(self, _area, cr, width, height):
        size = min(width, height)
        cx, cy, radius = width / 2, height / 2, size * 0.38
        cr.set_source_rgb(0.96, 0.98, 0.99)
        cr.paint()

        if self.mode == "digital":
            cr.set_source_rgb(0.10, 0.20, 0.28)
            cr.select_font_face("Sans", 0, 1)
            cr.set_font_size(max(28, size * 0.14))
            text = self.now.strftime("%H:%M:%S" if self.ticking else "%H:%M")
            extents = cr.text_extents(text)
            cr.move_to(cx - extents.width / 2, cy + extents.height / 2)
            cr.show_text(text)
            return

        cr.set_line_width(max(3, size * 0.012))
        cr.set_source_rgb(0.18, 0.53, 0.74)
        cr.arc(cx, cy, radius, 0, math.tau)
        cr.stroke()

        for mark in range(60):
            angle = mark * math.tau / 60 - math.pi / 2
            outer = radius * 0.94
            inner = radius * (0.86 if mark % 5 == 0 else 0.91)
            cr.set_line_width(max(2, size * (0.012 if mark % 5 == 0 else 0.006)))
            cr.move_to(cx + math.cos(angle) * inner, cy + math.sin(angle) * inner)
            cr.line_to(cx + math.cos(angle) * outer, cy + math.sin(angle) * outer)
            cr.stroke()

        if self.mode == "simple":
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

        seconds = self.now.second if self.ticking else 0
        hands = (
            (self.now.hour % 12 * 60 + self.now.minute, 720, radius * 0.52, 5, (0.00, 0.37, 0.89)),
            (self.now.minute * 60 + seconds, 3600, radius * 0.76, 4, (0.00, 0.70, 0.05)),
        )
        if self.ticking:
            hands += ((seconds, 60, radius * 0.84, 2, (0.90, 0.05, 0.04)),)
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


class ClockActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("What Time Is It?")
        self.mode = "simple"
        self.show_words = False
        self.show_date = False
        self.speak_time = False
        self.ticking = True
        self._mode_buttons = {}
        self._build()
        self._tick()
        GLib.timeout_add_seconds(1, self._tick)

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        for side in ("top", "bottom", "start", "end"):
            getattr(root, f"set_margin_{side}")(24)
        root.set_hexpand(True)
        root.set_vexpand(True)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["What Time Is It?"])
        root.set_accessible_role(Gtk.AccessibleRole.GROUP)

        title = Gtk.Label(label="What Time Is It?", xalign=0)
        title.add_css_class("title-2")
        root.append(title)

        mode_label = Gtk.Label(label="Clock style", xalign=0)
        mode_label.add_css_class("heading")
        root.append(mode_label)
        modes = Gtk.FlowBox()
        modes.set_selection_mode(Gtk.SelectionMode.NONE)
        modes.set_homogeneous(True)
        modes.set_column_spacing(8)
        modes.set_row_spacing(8)
        modes.set_max_children_per_line(3)
        modes.set_min_children_per_line(1)
        for mode, label in (("simple", "Simple"), ("nice", "Nice"), ("digital", "Digital")):
            button = Gtk.ToggleButton(label=label)
            button.set_hexpand(True)
            button.set_tooltip_text(f"Show the {label.lower()} clock")
            button.update_property([Gtk.AccessibleProperty.LABEL], [f"{label} clock"])
            button.connect("toggled", self._mode_changed, mode)
            if self._mode_buttons:
                button.set_group(next(iter(self._mode_buttons.values())))
            self._mode_buttons[mode] = button
            modes.insert(button, -1)
        root.append(modes)

        option_label = Gtk.Label(label="Display options", xalign=0)
        option_label.add_css_class("heading")
        root.append(option_label)
        options = Gtk.FlowBox()
        options.set_selection_mode(Gtk.SelectionMode.NONE)
        options.set_homogeneous(True)
        options.set_column_spacing(8)
        options.set_row_spacing(8)
        options.set_max_children_per_line(4)
        options.set_min_children_per_line(1)
        self._show_words_button = self._option(options, "Time in words", self._words_changed)
        self._show_date_button = self._option(options, "Weekday and date", self._date_changed)
        self._speak_button = self._option(options, "Speak each minute", self._speak_changed)
        self._ticking_button = self._option(options, "Ticking seconds", self._ticking_changed)
        self._adjust_button = self._option(options, "Adjust hands", self._adjust_changed)
        root.append(options)

        self.face = ClockFace()
        root.append(self.face)

        self.words = Gtk.Label(xalign=0.5)
        self.words.add_css_class("clock-words")
        self.words.set_wrap(True)
        self.words.set_visible(False)
        self.words.update_property([Gtk.AccessibleProperty.LABEL], ["Time in words"])
        root.append(self.words)

        self.date = Gtk.Label(xalign=0.5)
        self.date.add_css_class("clock-date")
        self.date.set_visible(False)
        self.date.update_property([Gtk.AccessibleProperty.LABEL], ["Weekday and date"])
        root.append(self.date)

        self.set_canvas(root)
        self.face.on_time_changed = self._manual_time_changed
        self._mode_buttons["simple"].set_active(True)
        provider = Gtk.CssProvider()
        provider.load_from_data(
            b".clock-date { font-size: 20px; } .clock-words { font-size: 20px; font-weight: 600; } "
            b"button { min-height: 42px; }"
        )
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    @staticmethod
    def _option(container, label, callback):
        button = Gtk.ToggleButton(label=label)
        button.set_hexpand(True)
        button.set_halign(Gtk.Align.FILL)
        button.update_property([Gtk.AccessibleProperty.LABEL], [label])
        button.connect("toggled", callback)
        container.insert(button, -1)
        return button

    def _mode_changed(self, button, mode):
        if not button.get_active():
            return
        self.mode = mode
        self._adjust_button.set_sensitive(mode != "digital")
        if mode == "digital" and self._adjust_button.get_active():
            self._adjust_button.set_active(False)
        self._refresh()

    def _words_changed(self, button):
        self.show_words = button.get_active()
        self.words.set_visible(self.show_words)
        self._refresh()

    def _date_changed(self, button):
        self.show_date = button.get_active()
        self.date.set_visible(self.show_date)
        self._refresh()

    def _speak_changed(self, button):
        self.speak_time = button.get_active()

    def _ticking_changed(self, button):
        self.ticking = button.get_active()
        self._refresh()

    def _adjust_changed(self, button):
        self.face.set_interactive(button.get_active())
        self._refresh()

    def _manual_time_changed(self, now):
        self.now = now
        self._refresh()

    def _tick(self):
        if not self.face.manual_time:
            self.now = datetime.now()
        self._refresh()
        if self.speak_time and self.now.second == 0:
            self._speak_now()
        return GLib.SOURCE_CONTINUE

    def _refresh(self):
        now = getattr(self, "now", datetime.now())
        self.face.update(now, self.mode, self.ticking)
        self.date.set_text(now.strftime("%A, %B %d, %Y"))
        self.words.set_text(self._time_in_words(now))

    @staticmethod
    def _time_in_words(now):
        hour = now.hour % 12 or 12
        if now.hour == 0 and now.minute == 0:
            return "midnight"
        if now.hour == 12 and now.minute == 0:
            return "noon"
        hour_word = WORDS[hour]
        period = "AM" if now.hour < 12 else "PM"
        minute_word = "o'clock" if now.minute == 0 else MINUTES[now.minute - 1]
        return f"{hour_word} {minute_word} {period}"

    def _speak_now(self):
        text = self._time_in_words(self.now)
        command = shutil.which("spd-say") or shutil.which("espeak")
        if command:
            try:
                subprocess.Popen([command, text], start_new_session=True)
            except OSError:
                pass

    def read_file(self, file_path):
        """Restore display choices from a Journal object without speaking."""
        try:
            state = json.loads(Path(file_path).read_text(encoding="utf-8"))
            if not isinstance(state, dict):
                raise ValueError("state must be an object")
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            state = {}
        mode = state.get("mode", "simple")
        self.mode = mode if mode in MODES else "simple"
        self.show_words = bool(state.get("show_words", False))
        self.show_date = bool(state.get("show_date", False))
        self.speak_time = bool(state.get("speak_time", False))
        self.ticking = bool(state.get("ticking", True))
        self._mode_buttons[self.mode].set_active(True)
        self._show_words_button.set_active(self.show_words)
        self._show_date_button.set_active(self.show_date)
        self._speak_button.set_active(self.speak_time)
        self._ticking_button.set_active(self.ticking)
        adjust_hands = bool(state.get("adjust_hands", False)) and self.mode != "digital"
        self._adjust_button.set_sensitive(self.mode != "digital")
        self._adjust_button.set_active(adjust_hands)
        self.words.set_visible(self.show_words)
        self.date.set_visible(self.show_date)
        self._refresh()

    def write_file(self, file_path):
        state = {
            "mode": self.mode,
            "show_date": self.show_date,
            "show_words": self.show_words,
            "speak_time": self.speak_time,
            "ticking": self.ticking,
            "adjust_hands": self.face.interactive,
        }
        Path(file_path).write_text(json.dumps(state, sort_keys=True) + "\n", encoding="utf-8")
