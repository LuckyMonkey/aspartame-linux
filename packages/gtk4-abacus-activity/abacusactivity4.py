"""Native GTK4 Abacus Activity.

A port of the GTK3 Abacus (sugarlabs/abacus): the same abacus types, beads
moved by clicking, a custom abacus, and copy/paste of the value. Bead state
lives in :mod:`abacus_model`; this module only draws it and handles input.

Keyboard: Left/Right choose a rod, Up/Down move one unit on it, digits set
it, and Shift+Down pushes a fraction bead below the rest line.
"""

import json
from pathlib import Path

from gi.repository import Gdk, Gtk

from abacus_model import (Abacus, CUSTOM_LIMITS, LABELS, TYPE_ORDER,
                          format_value, parse_value)
from sugar4.activity import SimpleActivity

BEAD_ACTIVE = (0.18, 0.53, 0.74)
BEAD_REST = (0.80, 0.84, 0.86)
# Cuisenaire rod colours, 1 to 10.
CUISENAIRE = ((0.96, 0.96, 0.94), (0.86, 0.20, 0.20), (0.55, 0.80, 0.30),
              (0.62, 0.36, 0.70), (0.98, 0.84, 0.20), (0.15, 0.50, 0.25),
              (0.15, 0.15, 0.15), (0.55, 0.35, 0.18), (0.20, 0.40, 0.80),
              (0.96, 0.55, 0.15))
TRISTATE_GAP = 2


def _slots(rod):
    """Bead positions below the bar: one spare, or two gaps on a tristate rod."""
    return rod.bottom + (2 * TRISTATE_GAP if rod.tristate else 1)


class AbacusActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Abacus")
        self.abacus = Abacus("suanpan")
        self.selected = len(self.abacus.rods) - 1
        self._layout = []
        self._build()
        self._refresh()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        root.set_margin_top(20); root.set_margin_bottom(20)
        root.set_margin_start(28); root.set_margin_end(28)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Abacus"])

        header = Gtk.Box(spacing=12)
        title = Gtk.Label(label="Abacus", xalign=0)
        title.add_css_class("abacus-title")
        title.set_hexpand(True)
        header.append(title)
        header.append(Gtk.Label(label="Type"))
        self.kind = Gtk.DropDown.new_from_strings([LABELS[n] for n in TYPE_ORDER])
        self.kind.update_property([Gtk.AccessibleProperty.LABEL], ["Abacus type"])
        self.kind.set_tooltip_text("Choose the kind of abacus")
        self.kind.connect("notify::selected", self._kind_changed)
        header.append(self.kind)
        root.append(header)

        self.custom = Gtk.Box(spacing=8)
        self._spins = {}
        for key in ("rods", "top", "bottom", "factor", "base"):
            low, high = CUSTOM_LIMITS[key]
            self.custom.append(Gtk.Label(label=key.capitalize()))
            spin = Gtk.SpinButton.new_with_range(low, high, 1)
            spin.set_value(self.abacus.custom[key])
            spin.update_property([Gtk.AccessibleProperty.LABEL], ["Custom %s" % key])
            self.custom.append(spin)
            self._spins[key] = spin
        build = Gtk.Button(label="Make abacus")
        build.set_tooltip_text("Build a custom abacus from these settings")
        build.connect("clicked", self._make_custom)
        self.custom.append(build)
        self.custom.set_visible(False)
        root.append(self.custom)

        self.value_label = Gtk.Label(label="0", xalign=0.5, selectable=True)
        self.value_label.add_css_class("abacus-value")
        self.value_label.update_property([Gtk.AccessibleProperty.LABEL], ["Abacus value"])
        root.append(self.value_label)

        self.area = Gtk.DrawingArea()
        self.area.set_hexpand(True); self.area.set_vexpand(True)
        self.area.set_content_height(360)
        self.area.set_focusable(True)
        self.area.set_draw_func(self._draw)
        self.area.update_property([Gtk.AccessibleProperty.LABEL], ["Abacus beads"])
        click = Gtk.GestureClick(button=0)
        click.connect("pressed", self._clicked)
        self.area.add_controller(click)
        keys = Gtk.EventControllerKey()
        keys.connect("key-pressed", self._key)
        self.area.add_controller(keys)
        frame = Gtk.Frame()
        frame.add_css_class("abacus-card")
        frame.set_child(self.area)
        root.append(frame)

        controls = Gtk.Box(spacing=8)
        controls.set_halign(Gtk.Align.CENTER)
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Number, e.g. 42 or 2 1/3")
        self.entry.update_property([Gtk.AccessibleProperty.LABEL], ["Number to show"])
        self.entry.connect("activate", self._show_number)
        controls.append(self.entry)
        for label, tip, handler in (
                ("Show number", "Move the beads to show this number", self._show_number),
                ("Copy value", "Copy the value to the clipboard", self._copy),
                ("Paste value", "Show the number on the clipboard", self._paste),
                ("Reset", "Move every bead back to rest", self._reset)):
            button = Gtk.Button(label=label)
            button.set_tooltip_text(tip)
            button.connect("clicked", handler)
            controls.append(button)
        root.append(controls)

        self.status = Gtk.Label(label="Click a bead, or use the arrow keys on the abacus.",
                                xalign=0, wrap=True)
        self.status.add_css_class("dim-label")
        self.status.update_property([Gtk.AccessibleProperty.LABEL], ["Abacus status"])
        root.append(self.status)
        self.set_canvas(root)

        provider = Gtk.CssProvider()
        provider.load_from_data(
            b"frame.abacus-card { border: 2px solid #8aa8b8; border-radius: 10px; }"
            b" label.abacus-title { font-size: 26px; font-weight: bold; }"
            b" label.abacus-value { font-size: 28px; font-weight: bold; color: #2f88bd; }"
            b" button { min-height: 40px; border-radius: 19px; }")
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    # Model changes

    def _set_kind(self, kind):
        self.abacus.set_type(kind)
        self.selected = len(self.abacus.rods) - 1
        self.custom.set_visible(kind == "custom")
        index = TYPE_ORDER.index(kind)
        if self.kind.get_selected() != index:
            self.kind.set_selected(index)
        self._refresh("%s abacus" % LABELS[kind])

    def _kind_changed(self, dropdown, _pspec):
        kind = TYPE_ORDER[dropdown.get_selected()]
        if kind != self.abacus.type.name:
            self._set_kind(kind)

    def _make_custom(self, _button):
        self.abacus.custom = {k: s.get_value_as_int() for k, s in self._spins.items()}
        try:
            self._set_kind("custom")
        except ValueError as error:
            self.status.set_text(str(error))

    def _refresh(self, message=None):
        text = self.abacus.value_text()
        self.value_label.set_text(text)
        self.value_label.update_property([Gtk.AccessibleProperty.DESCRIPTION],
                                         ["%s abacus showing %s" % (LABELS[self.abacus.type.name], text)])
        rod = self.abacus.type.rods[self.selected]
        self.area.update_property(
            [Gtk.AccessibleProperty.DESCRIPTION],
            ["Rod %d of %d, worth %s per bead, count %d" % (
                self.selected + 1, len(self.abacus.rods), format_value(rod.place, True),
                self.abacus.count(self.selected))])
        if message:
            self.status.set_text(message)
        self.area.queue_draw()

    def _show_number(self, _widget):
        try:
            self.abacus.set_value(parse_value(self.entry.get_text()))
        except ValueError as error:
            self.status.set_text("Cannot show that: %s" % error)
            return
        self._refresh("Showing %s" % self.abacus.value_text())

    def _copy(self, _button):
        self.get_clipboard().set(self.abacus.value_text().replace("−", "-"))
        self.status.set_text("Copied %s" % self.abacus.value_text())

    def _paste(self, _button):
        self.get_clipboard().read_text_async(None, self._pasted)

    def _pasted(self, clipboard, result):
        try:
            text = clipboard.read_text_finish(result) or ""
        except Exception as error:
            self.status.set_text("Nothing to paste: %s" % error)
            return
        self.entry.set_text(text.strip())
        self._show_number(None)

    def _reset(self, _button):
        self.abacus.clear()
        self._refresh("Reset")

    def _key(self, _controller, keyval, _keycode, state):
        rods = len(self.abacus.rods)
        if keyval in (Gdk.KEY_Left, Gdk.KEY_Right):
            step = -1 if keyval == Gdk.KEY_Left else 1
            self.selected = (self.selected + step) % rods
        elif keyval in (Gdk.KEY_Up, Gdk.KEY_Down):
            step = 1 if keyval == Gdk.KEY_Up else -1
            self.abacus.set_count(self.selected, self.abacus.count(self.selected) + step)
        elif Gdk.KEY_0 <= keyval <= Gdk.KEY_9:
            self.abacus.set_count(self.selected, keyval - Gdk.KEY_0)
        else:
            return False
        self._refresh()
        return True

    # Drawing: each rod is laid out once per draw and reused for hit tests.

    def _geometry(self, width, height):
        rods = self.abacus.type.rods
        top_slots = max(r.top for r in rods)
        bottom_slots = max(_slots(r) for r in rods)
        slots = (top_slots + 1 if top_slots else 0) + bottom_slots + 1
        pitch = min(width / (len(rods) + 1), 120)
        bead_h = min((height - 40) / slots, pitch * 0.6)
        left = (width - pitch * len(rods)) / 2
        top = (height - bead_h * slots - 24) / 2
        bar = top + (top_slots + 1) * bead_h if top_slots else top
        return pitch, bead_h, left, top, bar, top_slots

    def _beads(self, width, height):
        """Yield (rod, region, bead, x, y, w, h, active) for every bead."""
        pitch, bead_h, left, _top, bar, _top_slots = self._geometry(width, height)
        bead_w = min(pitch * 0.8, bead_h * 2.2)
        for i, rod in enumerate(self.abacus.type.rods):
            x = left + pitch * (i + 0.5) - bead_w / 2
            top, bottom = self.abacus.rods[i]
            for k in range(rod.top):
                gap = k if k < top else k + 1
                yield i, "top", k, x, bar - (gap + 1) * bead_h, bead_w, bead_h, k < top
            for k in range(rod.bottom):
                if rod.tristate:
                    # Resting beads sit mid-rod; counted beads move a clear
                    # gap up (positive) or down (negative).
                    slot = k + TRISTATE_GAP
                    if bottom > 0 and k < bottom:
                        slot = k
                    elif bottom < 0 and k >= rod.bottom + bottom:
                        slot = k + 2 * TRISTATE_GAP
                    active = slot != k + TRISTATE_GAP
                else:
                    slot = k if k < bottom else k + 1
                    active = k < bottom
                yield i, "bottom", k, x, bar + bead_h * 0.4 + slot * bead_h, bead_w, bead_h, active

    def _draw(self, _area, cr, width, height):
        pitch, bead_h, left, top, bar, top_slots = self._geometry(width, height)
        rods = self.abacus.type.rods
        frame_bottom = bar + bead_h * (max(_slots(r) for r in rods) + 0.8)
        cr.set_source_rgb(0.98, 0.97, 0.94)
        cr.rectangle(left - 8, top - 8, pitch * len(rods) + 16, frame_bottom - top + 16)
        cr.fill()
        cr.set_source_rgb(0.35, 0.27, 0.20)
        cr.set_line_width(6)
        cr.rectangle(left - 8, top - 8, pitch * len(rods) + 16, frame_bottom - top + 16)
        cr.stroke()
        for i in range(len(rods)):
            x = left + pitch * (i + 0.5)
            if i == self.selected:
                cr.set_source_rgba(0.18, 0.53, 0.74, 0.15)
                cr.rectangle(x - pitch / 2, top - 4, pitch, frame_bottom - top + 8)
                cr.fill()
            cr.set_source_rgb(0.45, 0.45, 0.45)
            cr.set_line_width(3)
            cr.move_to(x, top)
            cr.line_to(x, frame_bottom)
            cr.stroke()
        cr.set_source_rgb(0.35, 0.27, 0.20)
        cr.rectangle(left - 8, bar, pitch * len(rods) + 16, bead_h * 0.35)
        cr.fill()
        for i, region, k, x, y, w, h, active in self._beads(width, height):
            if self.abacus.type.colored:
                color = CUISENAIRE[(rods[i].bottom - 1) % 10]
                color = color if active else tuple(0.55 + c * 0.45 for c in color)
            else:
                color = BEAD_ACTIVE if active else BEAD_REST
            cr.set_source_rgb(*color)
            cr.save()
            cr.translate(x + w / 2, y + h / 2)
            cr.scale(w / 2, h / 2 * 0.9)
            cr.arc(0, 0, 1, 0, 6.2832)
            cr.restore()
            cr.fill_preserve()
            cr.set_source_rgb(0.2, 0.2, 0.2)
            cr.set_line_width(1)
            cr.stroke()
        cr.set_source_rgb(0.15, 0.2, 0.22)
        cr.select_font_face("Sans", 0, 0)
        cr.set_font_size(max(10, min(16, pitch / 3.5)))
        for i in range(len(rods)):
            text = str(self.abacus.count(i))
            extents = cr.text_extents(text)
            cr.move_to(left + pitch * (i + 0.5) - extents.width / 2, frame_bottom + 26)
            cr.show_text(text)
        self._layout = list(self._beads(width, height))

    def _clicked(self, gesture, _n, px, py):
        self.area.grab_focus()
        shifted = gesture.get_current_event_state() & Gdk.ModifierType.SHIFT_MASK
        down = gesture.get_current_button() == 3 or bool(shifted)
        for i, region, k, x, y, w, h, _active in self._layout:
            if x <= px <= x + w and y <= py <= y + h:
                self.selected = i
                self.abacus.click_bead(i, region, k, down=down)
                self._refresh()
                return

    # Journal

    def read_file(self, file_path):
        """Restore the abacus type and beads; refuse anything unrecognised."""
        payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
        abacus = Abacus.from_payload(payload)
        self.abacus = abacus
        for key, spin in self._spins.items():
            spin.set_value(abacus.custom[key])
        self._set_kind_view()

    def _set_kind_view(self):
        kind = self.abacus.type.name
        self.selected = len(self.abacus.rods) - 1
        self.custom.set_visible(kind == "custom")
        index = TYPE_ORDER.index(kind)
        if self.kind.get_selected() != index:
            # Selecting in the dropdown would rebuild an empty abacus.
            self.kind.handler_block_by_func(self._kind_changed)
            self.kind.set_selected(index)
            self.kind.handler_unblock_by_func(self._kind_changed)
        self._refresh("Restored %s abacus" % LABELS[kind])

    def write_file(self, file_path):
        """Save the type, custom settings and bead positions as JSON."""
        if self.metadata is not None:
            self.metadata["abacus"] = self.abacus.type.name
            self.metadata["value"] = self.abacus.value_text()
        Path(file_path).write_text(json.dumps(self.abacus.to_payload(), sort_keys=True) + "\n",
                                   encoding="utf-8")
