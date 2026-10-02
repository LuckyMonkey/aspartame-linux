"""GTK4 six-face rating control drawn with cairo (see ``wongbaker.py``).

Selection is one-or-none: choosing the selected face again clears it, because
"not rated" is a real answer.  Every face is a focusable toggle button with an
accessible name and tooltip, so the scale works without a pointer.
"""

import math
from gettext import gettext as _

import gi
from gi.repository import GObject, Gtk

try:
    gi.require_foreign('cairo')
    CAN_DRAW = True
except ImportError:  # PyGObject without its cairo bridge: show numbers
    CAN_DRAW = False

from cpsection.activities import wongbaker


FACE_SIZE = 40
# Calm green through amber to red; the face shape carries the meaning too,
# so the scale still reads in greyscale or for colour-blind users.
FACE_COLORS = {
    0: (0.40, 0.73, 0.42), 2: (0.62, 0.78, 0.36), 4: (0.93, 0.80, 0.30),
    6: (0.96, 0.62, 0.26), 8: (0.92, 0.43, 0.25), 10: (0.84, 0.26, 0.26),
}


def draw_face(cr, width, height, score, selected=False, dim=False):
    """Draw one face; ``score`` 0 smiles broadly, 10 frowns with tears."""
    size = min(width, height)
    cx, cy, radius = width / 2, height / 2, size / 2 - 2
    pain = score / 10.0
    alpha = 0.45 if dim else 1.0
    red, green, blue = FACE_COLORS[score]

    cr.set_source_rgba(red, green, blue, alpha)
    cr.arc(cx, cy, radius, 0, 2 * math.pi)
    cr.fill_preserve()
    cr.set_source_rgba(0.12, 0.12, 0.12, alpha)
    cr.set_line_width(3.0 if selected else 1.5)
    cr.stroke()

    eye_y, eye_dx, eye_r = cy - radius * 0.22, radius * 0.36, max(1.5, radius * 0.09)
    for side in (-1, 1):
        cr.arc(cx + side * eye_dx, eye_y, eye_r, 0, 2 * math.pi)
        cr.fill()
        # Brows tilt upward toward the centre as it hurts more.
        if pain > 0.3:
            brow_y = eye_y - radius * 0.22
            cr.move_to(cx + side * (eye_dx + radius * 0.16), brow_y)
            cr.line_to(cx + side * (eye_dx - radius * 0.16), brow_y - radius * 0.12 * pain)
            cr.stroke()

    # Mouth: a curve from a wide smile (pain 0) through flat to a frown.
    curve = (0.5 - pain) * 2  # +1 smile .. -1 frown
    mouth_y = cy + radius * 0.38
    half = radius * 0.42
    cr.move_to(cx - half, mouth_y - curve * radius * 0.05)
    cr.curve_to(cx - half / 2, mouth_y + curve * radius * 0.28,
                cx + half / 2, mouth_y + curve * radius * 0.28,
                cx + half, mouth_y - curve * radius * 0.05)
    cr.stroke()

    if score == 10:
        cr.set_source_rgba(0.30, 0.55, 0.90, alpha)
        for side in (-1, 1):
            x = cx + side * eye_dx
            cr.move_to(x, eye_y + eye_r * 2)
            cr.curve_to(x - eye_r * 1.4, eye_y + radius * 0.4,
                        x + eye_r * 1.4, eye_y + radius * 0.4,
                        x, eye_y + eye_r * 2)
            cr.fill()


class FaceRating(Gtk.Box):
    """Row of six faces; emits ``rating-changed`` with a score or -1 for none."""

    __gsignals__ = {
        'rating-changed': (GObject.SignalFlags.RUN_FIRST, None, (int,)),
    }

    def __init__(self, score=None, context=''):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self._buttons = {}
        self._updating = False
        self.set_accessible_role(Gtk.AccessibleRole.GROUP)
        self.update_property([Gtk.AccessibleProperty.LABEL],
                             [_('How much does %s hurt?') % context if context
                              else _('How much does it hurt?')])
        for value in wongbaker.SCORES:
            button = Gtk.ToggleButton()
            button.add_css_class('flat')
            button.add_css_class('aspartame-rating-face')
            if CAN_DRAW:
                area = Gtk.DrawingArea(content_width=FACE_SIZE, content_height=FACE_SIZE)
                area.set_draw_func(self._draw, value)
                button.set_child(area)
            else:
                button.set_label(str(value))
            description = '%d: %s' % (value, wongbaker.label(value))
            if context:
                description = '%s (%s)' % (description, context)
            button.set_tooltip_text(description)
            button.update_property(
                [Gtk.AccessibleProperty.LABEL, Gtk.AccessibleProperty.DESCRIPTION],
                [wongbaker.label(value), description])
            button.connect('toggled', self._toggled, value)
            self._buttons[value] = button
            self.append(button)
        self.set_score(score)

    def get_score(self):
        return next((value for value, button in self._buttons.items()
                     if button.get_active()), None)

    def get_buttons(self):
        return tuple(self._buttons.values())

    def set_score(self, score):
        self._updating = True
        try:
            for value, button in self._buttons.items():
                button.set_active(value == score)
        finally:
            self._updating = False
        self._redraw()

    def _toggled(self, button, value):
        if self._updating:
            return
        if button.get_active():
            self._updating = True
            try:
                for other_value, other in self._buttons.items():
                    if other_value != value:
                        other.set_active(False)
            finally:
                self._updating = False
        self._redraw()
        score = self.get_score()
        self.emit('rating-changed', -1 if score is None else score)

    def _redraw(self):
        for button in self._buttons.values():
            button.get_child().queue_draw()
            if button.get_active():
                button.add_css_class('aspartame-rating-selected')
            else:
                button.remove_css_class('aspartame-rating-selected')

    def _draw(self, area, cr, width, height, value):
        selected = self._buttons[value].get_active() if value in self._buttons else False
        anything = any(button.get_active() for button in self._buttons.values())
        draw_face(cr, width, height, value, selected=selected,
                  dim=anything and not selected)


class ScoreBadge(Gtk.Box):
    """Read-only face plus text, for side-by-side parity results."""

    def __init__(self, score, text):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        if CAN_DRAW:
            area = Gtk.DrawingArea(content_width=24, content_height=24)
            area.set_draw_func(lambda _a, cr, w, h: draw_face(cr, w, h, score))
            self.append(area)
        self.append(Gtk.Label(label=text, xalign=0))
        self.update_property([Gtk.AccessibleProperty.LABEL], [text])
