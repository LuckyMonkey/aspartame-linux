from gettext import gettext as _

from gi.repository import Gtk

from sugar3.graphics import style
from jarabe.controlpanel.sectionview import SectionView

from . import model


class ActivityManager(SectionView):
    """A small, inspectable Activity inventory inside Sugar Settings."""

    def __init__(self, activity_model, alerts):
        SectionView.__init__(self)
        self._model = activity_model
        self._rows = {}
        self.set_border_width(style.DEFAULT_SPACING * 2)
        self.set_spacing(style.DEFAULT_SPACING)

        title = Gtk.Label()
        title.set_markup('<b>%s</b>' % _('Activities'))
        title.set_xalign(0)
        self.pack_start(title, False, False, 0)

        description = Gtk.Label(label=_('Installed Activities. Rate them to record what needs attention.'))
        description.set_xalign(0)
        description.set_line_wrap(True)
        self.pack_start(description, False, False, 0)

        self._scroller = Gtk.ScrolledWindow()
        self._scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self._list = Gtk.ListBox()
        self._list.set_selection_mode(Gtk.SelectionMode.NONE)
        self._scroller.add(self._list)
        self.pack_start(self._scroller, True, True, 0)

        self._empty = Gtk.Label(label=_('No Activities were found.'))
        self._empty.set_xalign(0)
        self.pack_start(self._empty, False, False, 0)
        self.setup()

    def setup(self):
        for child in self._list.get_children():
            self._list.remove(child)
        self._rows = {}
        ratings = model.load_ratings()
        activities = model.list_activities()
        self._empty.set_visible(not activities)
        for activity in activities:
            row = self._make_row(activity, ratings.get(activity['id'], 0))
            self._list.add(row)
        self._list.show_all()

    def apply(self):
        for activity_id, combo in self._rows.values():
            rating = combo.get_active()
            if rating > 0:
                model.save_rating(activity_id, rating)

    def undo(self):
        self.setup()

    def _make_row(self, activity, rating):
        row = Gtk.ListBoxRow()
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=style.DEFAULT_SPACING)
        box.set_border_width(style.DEFAULT_SPACING)
        row.add(box)

        labels = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        labels.set_hexpand(True)
        name = Gtk.Label(label=activity['name'])
        name.set_xalign(0)
        name.set_tooltip_text(_('Activity name: %s') % activity['name'])
        labels.pack_start(name, False, False, 0)
        version = activity['version'] or _('version unknown')
        detail = Gtk.Label(label=_('%s • %s') % (version, activity['path']))
        detail.set_xalign(0)
        detail.set_ellipsize(3)
        labels.pack_start(detail, False, False, 0)
        box.pack_start(labels, True, True, 0)

        combo = Gtk.ComboBoxText()
        combo.append_text(_('Not rated'))
        for label in model.RATINGS:
            combo.append_text(label)
        combo.set_active(rating if 0 <= rating <= 5 else 0)
        combo.set_tooltip_text(_('Rate this Activity from broken to perfect.'))
        combo.connect('changed', self._rating_changed, activity['id'])
        box.pack_start(combo, False, False, 0)

        remove = Gtk.Button(label=_('Remove'))
        remove.set_tooltip_text(_('Remove this Activity for this user.'))
        remove.set_sensitive(activity['user'])
        if not activity['user']:
            remove.set_tooltip_text(_('System Activities cannot be removed from this user session.'))
        remove.connect('clicked', self._remove_clicked, activity)
        box.pack_start(remove, False, False, 0)

        self._rows[activity['id']] = (activity['id'], combo)
        return row

    def _rating_changed(self, combo, activity_id):
        rating = combo.get_active()
        if rating > 0:
            model.save_rating(activity_id, rating)

    def _remove_clicked(self, _button, activity):
        dialog = Gtk.MessageDialog(
            transient_for=self.get_toplevel(),
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text=_('Remove %s?') % activity['name'])
        dialog.format_secondary_text(_('The Activity will be moved to a recoverable local quarantine.'))
        response = dialog.run()
        dialog.destroy()
        if response != Gtk.ResponseType.OK:
            return
        try:
            model.remove_activity(activity['path'])
        except (OSError, PermissionError, ValueError) as error:
            error_dialog = Gtk.MessageDialog(
                transient_for=self.get_toplevel(),
                flags=Gtk.DialogFlags.MODAL,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.CLOSE,
                text=_('Activity could not be removed'))
            error_dialog.format_secondary_text(str(error))
            error_dialog.run()
            error_dialog.destroy()
            return
        self.setup()
