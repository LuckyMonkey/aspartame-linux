"""One lifecycle subscription shared by Home Favorites and List views."""

from gettext import gettext as _

from gi.repository import GObject, Gtk

from sugar4.graphics import style
from sugar4.graphics.xocolor import XoColor
from jarabe.model import shell
from jarabe.desktop.activitystate import Instance, select_instance


STATE_LABELS = {
    'stopped': _('Stopped'),
    'launching': _('Starting'),
    'running': _('Running'),
    'active': _('Current activity'),
}


class ActivityPresentation(GObject.GObject):
    __gsignals__ = {
        'changed': (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self):
        super().__init__()
        self.model = shell.get_model()
        self._handlers = {}
        self.model.connect('activity-added', self._added)
        self.model.connect('activity-removed', self._removed)
        self.model.connect('active-activity-changed', self._changed)
        self.model.zoom_level_changed.connect(self._zoom_changed)
        for activity in self.model:
            self._watch(activity)

    def _watch(self, activity):
        if activity not in self._handlers:
            self._handlers[activity] = activity.connect(
                'notify::launch-status', self._changed)

    def _added(self, model, activity):
        self._watch(activity)
        self.emit('changed')

    def _removed(self, model, activity):
        handler = self._handlers.pop(activity, None)
        if handler is not None:
            activity.disconnect(handler)
        self.emit('changed')

    def _changed(self, *args):
        self.emit('changed')

    def _zoom_changed(self, **kwargs):
        self.emit('changed')

    def state(self, bundle_id):
        statuses = {shell.Activity.LAUNCHING: 'launching',
                    shell.Activity.LAUNCHED: 'running',
                    shell.Activity.LAUNCH_FAILED: 'failed'}
        activities = list(self.model)
        records = [Instance(activity.get_activity_id(), activity.get_bundle_id(),
                            statuses[activity.get_launch_status()])
                   for activity in activities]
        current = self.model.get_active_activity()
        active_id = (current.get_activity_id() if current is not None and
                     self.model.zoom_level == self.model.ZOOM_ACTIVITY else None)
        state, activity_id = select_instance(bundle_id, records, active_id)
        activity = next((item for item in activities
                         if item.get_activity_id() == activity_id), None)
        return state, activity

    def present(self, icon, bundle_id):
        state, activity = self.state(bundle_id)
        color = (activity.get_icon_color() if activity is not None else
                 XoColor('%s,%s' % (style.COLOR_BUTTON_GREY.get_svg(),
                                   style.COLOR_WHITE.get_svg())))
        icon.props.xo_color = color
        for name in STATE_LABELS:
            css_class = 'activity-' + name
            if name == state:
                icon.add_css_class(css_class)
            else:
                icon.remove_css_class(css_class)
        icon.update_state([Gtk.AccessibleState.BUSY], [state == 'launching'])
        return state

    def activate_running(self, bundle_id):
        state, activity = self.state(bundle_id)
        if activity is None:
            return False
        self.model.activate_activity(activity)
        return True


_instance = None


def get_model():
    global _instance
    if _instance is None:
        _instance = ActivityPresentation()
    return _instance
