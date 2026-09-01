"""Reusable five-level face rating control for Sugar surfaces."""

import os

from gettext import gettext as _

from gi.repository import Gtk, GObject


RATING_LABELS = (_('Broken'), _('Bad'), _('Needs work'), _('Good'), _('Perfect'))
FACE_FILES = ('broken.svg', 'bad.svg', 'needs-work.svg', 'good.svg', 'perfect.svg')
FACE_ROOT = '/usr/share/aspartame/activity-manager/faces'


class FaceRating(Gtk.Box):
    """A reusable Sugar-style five-level rating control using face SVGs."""

    __gsignals__ = {
        'rating-changed': (GObject.SignalFlags.RUN_FIRST, None, (int,)),
    }

    def __init__(self, rating=0, context='', face_root=FACE_ROOT):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self._buttons = []
        self._context = context
        self._face_root = face_root
        for index, (filename, label) in enumerate(
                zip(FACE_FILES, RATING_LABELS), 1):
            # Toggle buttons allow the valid unanswered state: no face
            # selected. The toggled handler enforces one-or-none selection.
            button = Gtk.ToggleButton()
            button.set_relief(Gtk.ReliefStyle.NONE)
            button.set_can_focus(False)
            button.get_style_context().add_class('aspartame-rating-face')
            image_path = os.path.join(face_root, filename)
            if os.path.isfile(image_path):
                image = Gtk.Image.new_from_file(image_path)
                image.set_pixel_size(52)
                button.set_image(image)
                button.set_always_show_image(True)
            button.set_tooltip_text(_('%s%s') % (
                label, _(': %s') % context if context else ''))
            button.connect('toggled', self._button_toggled, index)
            self._buttons.append(button)
            self.pack_start(button, False, False, 0)
        self.set_rating(rating, emit=False)
        self._refresh_appearance()

    def get_rating(self):
        return next((index for index, button in enumerate(self._buttons, 1)
                     if button.get_active()), 0)

    def get_buttons(self):
        """Return the face buttons for help registration or inspection."""
        return tuple(self._buttons)

    def set_rating(self, rating, emit=False):
        rating = rating if rating in range(0, len(self._buttons) + 1) else 0
        for index, button in enumerate(self._buttons, 1):
            button.set_active(rating == index)
        self._refresh_appearance()
        if emit:
            self.emit('rating-changed', rating)

    def _button_toggled(self, button, _rating):
        if button.get_active():
            for other in self._buttons:
                if other is not button and other.get_active():
                    other.set_active(False)
        self._refresh_appearance()
        if button.get_active():
            self.emit('rating-changed', self.get_rating())

    def _refresh_appearance(self):
        for button in self._buttons:
            image = button.get_image()
            if image is not None:
                image.set_opacity(1.0 if button.get_active() else 0.50)
            context = button.get_style_context()
            if button.get_active():
                context.add_class('aspartame-rating-selected')
            else:
                context.remove_class('aspartame-rating-selected')
