"""GTK4-native Activity Manager inventory."""

from gettext import gettext as _

from gi.repository import Gtk

from jarabe.controlpanel.sectionview import SectionView

from cpsection.activities import wongbaker
from cpsection.activities.faces import FaceRating, ScoreBadge


class ActivityManager(SectionView):
    def __init__(self, activity_model, alerts):
        super().__init__()
        self._model = activity_model
        self._rows = []
        # Equal-width action buttons keep the face columns aligned row to row.
        self._action_width = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)
        self.set_spacing(12)
        self.set_margin_top(24)
        self.set_margin_bottom(24)
        self.set_margin_start(24)
        self.set_margin_end(24)

        title = Gtk.Label(label=_('Activity Manager'), xalign=0)
        title.add_css_class('heading')
        self.append(title)
        self.append(Gtk.Label(
            label=_('Installed activities. System activities are managed by the OS.'),
            xalign=0))
        hint = Gtk.Label(
            label=_('Rate each Activity with a face: how much does using it hurt? '
                    'Choose the same face again to clear your answer.'),
            xalign=0)
        hint.set_wrap(True)
        hint.set_opacity(0.78)
        self.append(hint)
        self._count = Gtk.Label(xalign=0)
        self.append(self._count)
        self._status = Gtk.Label(xalign=0)
        self._status.set_opacity(0.78)
        self._status.set_wrap(True)
        self.append(self._status)

        scroller = Gtk.ScrolledWindow()
        scroller.set_vexpand(True)
        self._list = Gtk.ListBox()
        self._list.set_selection_mode(Gtk.SelectionMode.NONE)
        scroller.set_child(self._list)
        self.append(scroller)
        self.setup()

    def setup(self):
        while (child := self._list.get_row_at_index(0)) is not None:
            self._list.remove(child)
        self._rows = self._model.list_activities()
        ratings = self._model.load_ratings()
        port_status = self._model.load_port_status()
        self._count.set_text(_('%d installed activities') % len(self._rows))
        for activity in self._rows:
            row = Gtk.ListBoxRow()
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            box.set_margin_top(8)
            box.set_margin_bottom(8)
            box.set_margin_start(12)
            box.set_margin_end(12)
            info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            info.set_hexpand(True)
            info.append(Gtk.Label(label=activity['name'], xalign=0))
            info.append(Gtk.Label(
                label=_('Version %s · %s') % (
                    activity['version'],
                    _('System-managed') if activity['managed']
                    else _('User-installed')), xalign=0))
            status = port_status.get(activity['id'])
            if status:
                info.append(self._port_line(status))
            box.append(info)
            faces = FaceRating(score=ratings.get(activity['id']),
                               context=activity['name'])
            faces.connect('rating-changed', self._rating_changed, activity)
            box.append(faces)
            action = Gtk.Button(label=_('Request approval') if activity['managed']
                                else _('Remove'))
            action.set_sensitive(True)
            action.set_tooltip_text(
                _('Request Sugar approval to remove this system Activity.')
                if activity['managed'] else
                _('Remove this Activity to a recoverable quarantine.'))
            action.update_property(
                [Gtk.AccessibleProperty.LABEL,
                 Gtk.AccessibleProperty.DESCRIPTION],
                [action.get_label(), action.get_tooltip_text()])
            action.connect('clicked', self._remove_clicked, activity)
            self._action_width.add_widget(action)
            box.append(action)
            row.set_child(box)
            row.update_property([Gtk.AccessibleProperty.LABEL,
                                 Gtk.AccessibleProperty.DESCRIPTION],
                                [activity['name'], activity['id']])
            row.set_accessible_role(Gtk.AccessibleRole.LIST_ITEM)
            self._list.append(row)

    def _port_line(self, status):
        line = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        port_class = Gtk.Label(label=status.get('class', ''), xalign=0)
        port_class.add_css_class('dim-label')
        line.append(port_class)
        parity = status.get('parity')
        if parity and parity.get('score') is not None:
            score = parity['score']
            line.append(ScoreBadge(score, _('Side-by-side %s: %s') % (
                parity.get('date', ''), wongbaker.label(score))))
        elif parity:
            line.append(Gtk.Label(
                label=_('Side-by-side in progress (%s)') % parity.get('progress', ''),
                xalign=0))
        else:
            line.append(Gtk.Label(label=_('Not yet compared with GTK3'), xalign=0))
        return line

    def _rating_changed(self, _faces, score, activity):
        score = None if score < 0 else score
        try:
            self._model.save_rating(activity['id'], score)
        except (OSError, ValueError) as error:
            self._status.set_text(_('Rating not saved: %s') % error)
            return
        if score is None:
            self._status.set_text(_('Cleared your rating for %s.') % activity['name'])
        else:
            self._status.set_text(_('Rated %s: %s.') % (
                activity['name'], wongbaker.label(score)))

    def apply(self):
        return None

    def _remove_clicked(self, _button, activity):
        try:
            target = self._model.remove_activity(activity['path'])
        except (OSError, PermissionError, ValueError) as error:
            self._status.set_text(_('Removal not completed: %s') % error)
            return
        self._status.set_text(
            _('Removed %s. A recoverable copy is at %s.') %
            (activity['name'], target))
        self.setup()

    def undo(self):
        self.setup()
