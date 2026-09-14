"""GTK4 Journal ObjectChooser compatibility surface.

Activities use this class to select a Journal object.  The chooser keeps the
classic response/selected-id contract while using the native GTK4 Journal
ListView and its existing datastore adapter.
"""

from gettext import gettext as _

from gi.repository import GObject, Gtk

from jarabe.journal.listview import ListView


# Keep this value local: importing sugar3.graphics.objectchooser would load
# GTK3 into the modern process and violate the GTK3/GTK4 boundary.
FILTER_TYPE_MIME_BY_ACTIVITY = 'mime-by-activity'


class ObjectChooser(Gtk.Window):
    __gtype_name__ = 'ObjectChooser'

    __gsignals__ = {
        'response': (GObject.SignalFlags.RUN_FIRST, None, (int,)),
    }

    def __init__(self, parent=None, what_filter='', filter_type=None,
                 show_preview=False):
        super().__init__(title=_('Choose an object'))
        self._selected_object_id = None
        self._list_view = ListView(None)
        self.set_modal(parent is not None)
        if parent is not None:
            self.set_transient_for(parent)
        self.set_default_size(960, 640)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        root.set_margin_top(16)
        root.set_margin_bottom(16)
        root.set_margin_start(16)
        root.set_margin_end(16)
        self.set_child(root)

        header = Gtk.CenterBox()
        heading = Gtk.Label(label=_('Choose an object'), xalign=0)
        heading.add_css_class('heading')
        header.set_start_widget(heading)
        close = Gtk.Button(label=_('Cancel'))
        close.connect('clicked', self._cancel)
        header.set_end_widget(close)
        root.append(header)

        self._search = Gtk.SearchEntry(placeholder_text=_('Search Journal'))
        self._search.connect('search-changed', self._search_changed)
        root.append(self._search)

        self._list_view.connect('detail-clicked', self._entry_activated)
        root.append(self._list_view)

        key = Gtk.EventControllerKey()
        key.connect('key-pressed', self._key_pressed)
        self.add_controller(key)
        if what_filter and filter_type == FILTER_TYPE_MIME_BY_ACTIVITY:
            self._search.set_placeholder_text(
                _('Search objects for this Activity'))

    def _entry_activated(self, _view, uid):
        self._selected_object_id = str(uid)
        self.emit('response', Gtk.ResponseType.ACCEPT)

    def _cancel(self, _button):
        self.emit('response', Gtk.ResponseType.DELETE_EVENT)

    def _key_pressed(self, _controller, keyval, _keycode, _state):
        if keyval == 65307:  # Escape; avoids GTK-version-specific constants.
            self._cancel(None)
            return True
        return False

    def _search_changed(self, entry):
        text = entry.get_text().strip()
        self._list_view.update_with_query({'query': text} if text else {})

    def get_selected_object_id(self):
        return self._selected_object_id


ChooserListView = ListView
