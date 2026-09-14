"""GTK4-native Activity Manager inventory."""

from gettext import gettext as _

from gi.repository import Gtk

from jarabe.controlpanel.sectionview import SectionView


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
            box.append(info)
            action = Gtk.Button(label=_('Remove'))
            action.set_sensitive(not activity['managed'])
            action.set_tooltip_text(
                _('System activities cannot be removed here.')
                if activity['managed'] else
                _('Removal will require approval in a future Activity Manager pass.'))
            box.append(action)
            row.set_child(box)
            row.update_property([Gtk.AccessibleProperty.LABEL,
                                 Gtk.AccessibleProperty.DESCRIPTION],
                                [activity['name'], activity['id']])
            row.set_accessible_role(Gtk.AccessibleRole.LIST_ITEM)
            self._list.append(row)

    def apply(self):
        return None

    def undo(self):
        self.setup()
