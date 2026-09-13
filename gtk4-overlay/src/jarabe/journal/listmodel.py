# Copyright (C) 2026 Aspartame contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""A GTK-independent Gio.ListModel over the existing Journal datastore adapter.

The ResultSet retains datastore ordering, query language and volume behavior.
Rows are read in bounded idle batches. GTK creates widgets only for rows near
the viewport; scrolling never invokes a cell renderer or a datastore lookup.
"""

import logging

import dbus
from gi.repository import Gio, GLib, GObject

from jarabe.journal import model
from jarabe.journal.entrymodel import EntrySelection, normalized_query

_LOG = logging.getLogger(__name__)


class JournalEntry(GObject.Object):
    """Identity and metadata are separate from the presentation widget."""

    __gtype_name__ = 'AspartameJournalEntry'

    def __init__(self, metadata):
        super().__init__()
        self.metadata = dict(metadata)
        self.uid = str(self.metadata['uid'])


def write_metadata(metadata, ready_callback, error_callback):
    """Report async persistence failures to the UI instead of hiding them."""
    if metadata.get('mountpoint', '/') != '/':
        try:
            model.write(metadata, update_mtime=False,
                        ready_callback=lambda *args: ready_callback())
        except (OSError, ValueError, dbus.DBusException) as error:
            error_callback(error)
        return
    try:
        model._call_datastore(
            'update', metadata['uid'], dbus.Dictionary(metadata), '', False,
            reply_handler=ready_callback, error_handler=error_callback)
    except (ValueError, dbus.DBusException) as error:
        error_callback(error)


class ListModel(GObject.Object, Gio.ListModel):
    __gtype_name__ = 'AspartameJournalListModel'

    __gsignals__ = {
        'ready': (GObject.SignalFlags.RUN_FIRST, None, ()),
        'progress': (GObject.SignalFlags.RUN_FIRST, None, ()),
        'failed': (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        'selection-changed': (GObject.SignalFlags.RUN_FIRST, None, (int,)),
    }

    # Kept as metadata constants for out-of-process/legacy consumers. GTK4
    # presentation uses JournalEntry, never tree iterators or column indices.
    COLUMN_UID = 0
    COLUMN_FAVORITE = 1
    COLUMN_ICON = 2
    COLUMN_ICON_COLOR = 3
    COLUMN_TITLE = 4
    COLUMN_TIMESTAMP = 5
    COLUMN_CREATION_TIME = 6
    COLUMN_FILESIZE = 7
    COLUMN_PROGRESS = 8
    COLUMN_BUDDY_1 = 9
    COLUMN_BUDDY_2 = 10
    COLUMN_BUDDY_3 = 11
    COLUMN_SELECT = 12
    _PAGE_SIZE = 48

    def __init__(self, query, result_set_factory=None):
        super().__init__()
        self.query = normalized_query(query)
        factory = result_set_factory or model.find
        self._result_set = factory(normalized_query(self.query), self._PAGE_SIZE)
        self._entries = []
        self._ids = set()
        self._selection = EntrySelection()
        self._source = 0
        self._stopped = False
        self._position = 0
        self._total = 0
        self._result_set.ready.connect(self._result_ready)
        self._result_set.progress.connect(self._result_progress)

    def do_get_item_type(self):
        return JournalEntry

    def do_get_n_items(self):
        return len(self._entries)

    def do_get_item(self, position):
        return self._entries[position] if position < len(self._entries) else None

    def __len__(self):
        return len(self._entries)

    def __getitem__(self, position):
        return self._entries[position]

    def setup(self, updated_callback=None):
        try:
            self._result_set.setup()
        except (OSError, ValueError, dbus.DBusException) as error:
            self._fail(error)

    def _result_ready(self, **kwargs):
        if self._stopped:
            return
        try:
            self._total = self._result_set.length
        except (OSError, ValueError, dbus.DBusException) as error:
            self._fail(error)
            return
        self._source = GLib.idle_add(self._read_batch)

    def _read_batch(self):
        if self._stopped:
            self._source = 0
            return GLib.SOURCE_REMOVE
        first = len(self._entries)
        try:
            for _ in range(min(self._PAGE_SIZE, self._total - self._position)):
                self._result_set.seek(self._position)
                metadata = self._result_set.read()
                self._position += 1
                uid = str(metadata.get('uid', ''))
                if not uid or uid in self._ids:
                    _LOG.warning('Journal result has missing/duplicate UID: %r', uid)
                    continue
                self._ids.add(uid)
                self._entries.append(JournalEntry(metadata))
        except (OSError, ValueError, IndexError, dbus.DBusException) as error:
            self._source = 0
            self._fail(error)
            return GLib.SOURCE_REMOVE
        added = len(self._entries) - first
        if added:
            self.items_changed(first, 0, added)
        self.emit('progress')
        if self._position >= self._total:
            self._source = 0
            self.emit('ready')
            return GLib.SOURCE_REMOVE
        return GLib.SOURCE_CONTINUE

    def _result_progress(self, **kwargs):
        if not self._stopped:
            self.emit('progress')

    def _fail(self, error):
        _LOG.error('Journal query failed: %s', error)
        self.emit('failed', str(error))

    def stop(self):
        self._stopped = True
        if self._source:
            GLib.source_remove(self._source)
            self._source = 0
        self._result_set.stop()
        self._result_set.ready.disconnect(self._result_ready)
        self._result_set.progress.disconnect(self._result_progress)

    def get_metadata(self, position):
        return model.get(self._entries[position].uid)

    def get_all_ids(self):
        return [entry.uid for entry in self._entries]

    def set_selected(self, uid, value):
        if uid in self._ids:
            self._selection.set(uid, value)
            self.emit('selection-changed', len(self.get_selected_items()))

    def is_selected(self, uid):
        return self._selection.contains(uid)

    def get_selected_items(self):
        return self._selection.in_order(self.get_all_ids())

    def restore_selection(self, selected):
        self._selection.restore(selected, self.get_all_ids())
        self.emit('selection-changed', len(self.get_selected_items()))

    def select_all(self):
        self.restore_selection(self.get_all_ids())

    def select_none(self):
        self._selection.clear()
        self.emit('selection-changed', 0)
