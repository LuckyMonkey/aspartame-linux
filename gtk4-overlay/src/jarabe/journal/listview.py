"""GTK4-native Journal presentation for Aspartame.

The classic Journal TreeView remains in the GTK3 source tree.  GTK4 uses a
ListBox-backed surface so datastore entries are real GTK4 widgets rather than
legacy cell renderers.
"""

import logging
from gettext import gettext as _

from gi.repository import GObject, Gtk, GLib

from jarabe.journal import model

_LOG = logging.getLogger(__name__)


class _JournalRows(Gtk.ListBox):
    __gsignals__ = {
        'choose-project': (GObject.SignalFlags.RUN_FIRST, None, (object,)),
    }


class ListView(Gtk.Box):
    __gsignals__ = {
        'clear-clicked': (GObject.SignalFlags.RUN_FIRST, None, ()),
        'selection-changed': (GObject.SignalFlags.RUN_FIRST, None, (int,)),
        'detail-clicked': (GObject.SignalFlags.RUN_FIRST, None, (object,)),
        'volume-error': (GObject.SignalFlags.RUN_FIRST, None, (str, str)),
        'title-edit-started': (GObject.SignalFlags.RUN_FIRST, None, ()),
        'title-edit-finished': (GObject.SignalFlags.RUN_FIRST, None, (str, object)),
        'title-edit-canceled': (GObject.SignalFlags.RUN_FIRST, None, ()),
        'project-view-activate': (GObject.SignalFlags.RUN_FIRST, None, (object,)),
    }

    def __init__(self, journalactivity, enable_multi_operations=False):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self._query = {}
        self._rows = {}
        self._journalactivity = journalactivity
        self.tree_view = _JournalRows()
        self.tree_view.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.tree_view.connect('row-activated', self._row_activated)
        scroller = Gtk.ScrolledWindow()
        scroller.set_vexpand(True)
        scroller.set_child(self.tree_view)
        self.append(scroller)
        self._empty = Gtk.Label(label=_('Your Journal is empty'))
        self._empty.set_margin_top(48)
        self._empty.set_visible(False)
        self.append(self._empty)
        GLib.idle_add(self._refresh)

    def _refresh(self):
        while (row := self.tree_view.get_row_at_index(0)) is not None:
            self.tree_view.remove(row)
        self._rows.clear()
        try:
            result = model.find(self._query, 48)
            total = result.get_length()
            for index in range(total):
                result.seek(index)
                metadata = result.read()
                uid = str(metadata.get('uid', ''))
                if not uid:
                    continue
                row = Gtk.ListBoxRow()
                row._journal_uid = uid
                box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
                box.set_margin_start(24)
                box.set_margin_end(24)
                box.set_margin_top(10)
                box.set_margin_bottom(10)
                box.append(Gtk.Label(label=str(metadata.get('title') or _('Untitled')), xalign=0))
                box.append(Gtk.Label(label=str(metadata.get('activity') or ''), xalign=0))
                row.set_child(box)
                self.tree_view.append(row)
                self._rows[uid] = row
            self._empty.set_visible(total == 0)
        except Exception as error:
            _LOG.exception('GTK4 Journal refresh failed')
            self._empty.set_text(_('Journal unavailable: %s') % error)
            self._empty.set_visible(True)
        return GLib.SOURCE_REMOVE

    def _row_activated(self, _list, row):
        uid = getattr(row, '_journal_uid', None)
        if uid:
            self.emit('detail-clicked', uid)

    def update_with_query(self, query_dict):
        self._query = dict(query_dict or {})
        GLib.idle_add(self._refresh)

    def get_projects_view_active(self): return False
    def is_dragging(self): return False
    def set_is_visible(self, _visible): pass
    def get_model(self): return None
    def get_selected_items(self): return []
    def select_all(self): pass
    def select_none(self): pass


# ObjectChooser imports the historical base name; the GTK4 surface provides
# the same signal/method contract for chooser callers.
BaseListView = ListView
