"""GTK4-native Journal presentation for Aspartame.

The classic Journal TreeView remains in the GTK3 source tree.  GTK4 uses a
ListBox-backed surface so datastore entries are real GTK4 widgets rather than
legacy cell renderers.
"""

import logging
from gettext import gettext as _

from gi.repository import GObject, Gtk, GLib, Gdk

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
        self._dragging = False
        self._journalactivity = journalactivity
        self.tree_view = _JournalRows()
        self.tree_view.set_selection_mode(
            Gtk.SelectionMode.MULTIPLE if enable_multi_operations
            else Gtk.SelectionMode.SINGLE)
        self.tree_view.connect('row-activated', self._row_activated)
        self.tree_view.connect('selected-rows-changed', self._selection_changed)
        self._result_status = Gtk.Label(label=_('Journal entries'))
        self._result_status.set_xalign(0)
        self._result_status.set_margin_start(24)
        self._result_status.set_margin_top(8)
        self._result_status.set_opacity(0.72)
        self.append(self._result_status)
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
            query_text = str(self._query.get('query', '')).strip()
            if query_text:
                self._result_status.set_text(
                    _('%d matches for “%s”') % (total, query_text))
            else:
                self._result_status.set_text(
                    _('%d Journal entries') % total if total != 1
                    else _('1 Journal entry'))
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
                title = str(metadata.get('title') or _('Untitled'))
                activity = str(metadata.get('activity') or '')
                box.append(Gtk.Label(label=title, xalign=0))
                box.append(Gtk.Label(label=activity, xalign=0))
                row.set_child(box)
                drag_source = Gtk.DragSource()
                drag_source.set_actions(Gdk.DragAction.COPY)
                drag_source.connect('prepare', self._prepare_drag, uid)
                drag_source.connect('drag-begin', self._drag_begin)
                drag_source.connect('drag-end', self._drag_end)
                drag_source.connect('drag-cancel', self._drag_cancel)
                row.add_controller(drag_source)
                row.update_property([Gtk.AccessibleProperty.LABEL,
                                     Gtk.AccessibleProperty.DESCRIPTION],
                                    [title, activity])
                row.set_accessible_role(Gtk.AccessibleRole.LIST_ITEM)
                self.tree_view.append(row)
                self._rows[uid] = row
            self._empty.set_visible(total == 0)
        except Exception as error:
            _LOG.exception('GTK4 Journal refresh failed')
            self._result_status.set_text(_('Journal search unavailable'))
            self._empty.set_text(_('Journal unavailable: %s') % error)
            self._empty.set_visible(True)
        return GLib.SOURCE_REMOVE

    def _row_activated(self, _list, row):
        uid = getattr(row, '_journal_uid', None)
        if uid:
            # Defer canvas replacement until the ListBox activation dispatch
            # has completed; swapping a rooted child synchronously triggers
            # GTK's gtk_widget_root assertion in the GTK4 preview.
            GLib.idle_add(self._activate_detail, uid)

    def _selection_changed(self, _list):
        self.emit('selection-changed', len(self.get_selected_items()))

    def _activate_detail(self, uid):
        self.emit('detail-clicked', uid)
        return GLib.SOURCE_REMOVE

    def _prepare_drag(self, _source, _x, _y, uid):
        payload = GLib.Bytes.new(str(uid).encode('utf-8'))
        return Gdk.ContentProvider.new_for_bytes('text/plain', payload)

    def _drag_begin(self, *_args):
        self._dragging = True

    def _drag_end(self, *_args):
        self._dragging = False

    def _drag_cancel(self, *_args):
        self._dragging = False

    def update_with_query(self, query_dict):
        self._query = dict(query_dict or {})
        GLib.idle_add(self._refresh)

    def get_projects_view_active(self): return False
    def is_dragging(self): return self._dragging
    def set_is_visible(self, _visible): return None
    def get_model(self): return self

    def __len__(self):
        return len(self._rows)

    def set_selected(self, uid, value):
        row = self._rows.get(str(uid))
        if row is None:
            return
        if value:
            self.tree_view.select_row(row)
        else:
            self.tree_view.unselect_row(row)

    def get_selected_items(self):
        return [getattr(row, '_journal_uid', None)
                for row in self.tree_view.get_selected_rows()
                if getattr(row, '_journal_uid', None)]

    def select_all(self):
        if self.tree_view.get_selection_mode() == Gtk.SelectionMode.MULTIPLE:
            for row in self._rows.values():
                self.tree_view.select_row(row)
        elif self._rows:
            self.tree_view.select_row(next(iter(self._rows.values())))
        self.emit('selection-changed', len(self.get_selected_items()))

    def select_none(self):
        self.tree_view.unselect_all()
        self.emit('selection-changed', 0)

    def get_metadata(self, uid):
        return model.get(str(uid))


# ObjectChooser imports the historical base name; the GTK4 surface provides
# the same signal/method contract for chooser callers.
BaseListView = ListView
