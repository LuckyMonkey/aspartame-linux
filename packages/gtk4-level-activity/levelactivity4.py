"""GTK4-native, offline spirit-level Activity.

The original Level Activity reads device orientation when hardware provides it.
This implementation keeps the useful measurement interaction available on
desktops and VMs: drag the bubble or use the arrow controls to set inclination.
"""

import json

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class LevelActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Level")
        self.angle = 0

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        root.set_margin_top(32); root.set_margin_bottom(32)
        root.set_margin_start(40); root.set_margin_end(40)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Level"])
        root.set_accessible_role(Gtk.AccessibleRole.GROUP)
        title = Gtk.Label(label="Level", xalign=0)
        title.add_css_class("title-1")
        root.append(title)
        self.readout = Gtk.Label(xalign=0)
        self.readout.update_property([Gtk.AccessibleProperty.LABEL], ["Inclination"])
        root.append(self.readout)

        self.canvas = Gtk.DrawingArea()
        self.canvas.set_content_width(700); self.canvas.set_content_height(260)
        self.canvas.set_hexpand(True); self.canvas.set_vexpand(True)
        self.canvas.set_draw_func(self._draw)
        # GTK4 has no IMAGE accessible role; the custom drawing surface is a
        # labelled group containing the level controls and canvas.
        self.canvas.set_accessible_role(Gtk.AccessibleRole.GROUP)
        self.canvas.update_property([Gtk.AccessibleProperty.LABEL], ["Spirit level"])
        drag = Gtk.GestureDrag()
        drag.connect("drag-update", self._drag_update)
        self.canvas.add_controller(drag)
        root.append(self.canvas)

        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10,
                           halign=Gtk.Align.CENTER)
        self._button(controls, "←", self._nudge_left, "Decrease inclination")
        reset = self._button(controls, "Reset", self._reset, "Reset level")
        reset.add_css_class("suggested-action")
        self._button(controls, "→", self._nudge_right, "Increase inclination")
        root.append(controls)
        self.set_canvas(root)
        self._install_css()
        self._render()

    def _button(self, parent, label, callback, accessible):
        button = Gtk.Button(label=label)
        button.set_size_request(74, 46)
        button.update_property([Gtk.AccessibleProperty.LABEL], [accessible])
        button.connect("clicked", callback)
        parent.append(button)
        return button

    def _install_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(b"""
            .level-readout { font-size: 24px; font-weight: bold; }
            button { min-height: 42px; border-radius: 20px; }
        """)
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _render(self):
        self.readout.set_text("%+d° inclination" % self.angle)
        self.readout.add_css_class("level-readout")
        self.canvas.queue_draw()

    def _draw(self, _area, cr, width, height):
        cx, cy = width / 2, height / 2
        cr.set_source_rgb(.86, .89, .90); cr.paint()
        cr.save(); cr.translate(cx, cy); cr.rotate(self.angle * 3.14159 / 180)
        cr.set_source_rgb(.25, .29, .31); cr.set_line_width(14)
        cr.move_to(-width * .38, 0); cr.line_to(width * .38, 0); cr.stroke()
        cr.set_source_rgb(.25, .55, .75); cr.set_line_width(5)
        cr.move_to(-width * .38, 0); cr.line_to(width * .38, 0); cr.stroke()
        cr.restore()
        cr.set_source_rgb(.1, .1, .1); cr.set_line_width(3)
        cr.arc(cx, cy, 24, 0, 2 * 3.14159); cr.stroke()
        cr.set_source_rgb(.25, .55, .75)
        cr.arc(cx + self.angle * 3, cy, 13, 0, 2 * 3.14159); cr.fill()

    def _drag_update(self, _gesture, _offset_x, offset_y):
        self.angle = max(-45, min(45, int(-offset_y / 3)))
        self._render()

    def _nudge_left(self, *_args):
        self.angle = max(-45, self.angle - 1); self._render()

    def _nudge_right(self, *_args):
        self.angle = min(45, self.angle + 1); self._render()

    def _reset(self, *_args):
        self.angle = 0; self._render()

    def write_file(self, file_path):
        with open(file_path, "w", encoding="utf-8") as stream:
            json.dump({"angle": self.angle}, stream)

    def read_file(self, file_path):
        with open(file_path, encoding="utf-8") as stream:
            state = json.load(stream)
        self.angle = max(-45, min(45, int(state.get("angle", 0))))
        self._render()
