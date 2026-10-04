"""GTK4-native Activity Manager inventory."""

from gettext import gettext as _

from gi.repository import Gtk

from jarabe.controlpanel.sectionview import SectionView


RUNTIME_LABELS = {
    'native-sugar': _('Native Sugar'),
    'snakepit-python': _('Snakepit Python'),
    'sugarizer-web': _('Sugarizer web'),
    'aspartame-native': _('Aspartame native'),
    'experimental': _('Experimental'),
}


class ActivityManager(SectionView):
    def __init__(self, activity_model, alerts):
        super().__init__()
        self._model = activity_model
        self._rows = []
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
        installed = [activity for activity in self._rows
                     if activity.get('installed', False)]
        self._count.set_text(_('%d installed activities') % len(installed))
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
            runtime = RUNTIME_LABELS.get(
                activity.get('runtime', 'experimental'),
                _('Unknown runtime'))
            install_state = (_('System-managed') if activity['managed']
                             else _('User-installed'))
            display_state = _('%s · %s') % (runtime, install_state)
            info.append(Gtk.Label(
                label=_('%s · Version %s · %s') % (
                    runtime, activity['version'], install_state), xalign=0))
            box.append(info)
            removable = activity.get('removable', False)
            if removable:
                action_label = (_('Request approval') if activity['managed']
                                else _('Remove'))
                action_tip = (
                    _('Request Sugar approval to remove this system Activity.')
                    if activity['managed'] else
                    _('Remove this Activity to a recoverable quarantine.'))
            else:
                action_label = _('Unavailable')
                action_tip = _('No qualified launch or removal action is available.')
            action = Gtk.Button(label=action_label)
            action.set_sensitive(removable)
            action.set_tooltip_text(action_tip)
            action.update_property(
                [Gtk.AccessibleProperty.LABEL,
                 Gtk.AccessibleProperty.DESCRIPTION],
                [action.get_label(), action.get_tooltip_text()])
            action.connect('clicked', self._remove_clicked, activity)
            box.append(action)
            row.set_child(box)
            row.update_property([Gtk.AccessibleProperty.LABEL,
                                 Gtk.AccessibleProperty.DESCRIPTION],
                                [activity['name'], display_state])
            row.set_accessible_role(Gtk.AccessibleRole.LIST_ITEM)
            self._list.append(row)

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
