"""GTK4-native Journal presentation for Aspartame.

The classic Journal TreeView remains in the GTK3 source tree.  GTK4 uses a
ListBox-backed surface so datastore entries are real GTK4 widgets rather than
legacy cell renderers.
"""

import logging
from gettext import gettext as _

from gi.repository import GObject, Gtk, GLib, Gdk

from jarabe.journal import model
from jarabe.journal.entrymodel import editable_changes
from jarabe.journal.listmodel import write_metadata

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
        self._projects_only = False
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
        self._projects_button = Gtk.ToggleButton(label=_('Projects'))
        self._projects_button.set_tooltip_text(_('Show Journal entries assigned to a project'))
        self._projects_button.update_property([Gtk.AccessibleProperty.LABEL], [_('Show project entries')])
        self._projects_button.connect('toggled', self._projects_toggled)
        self.append(self._projects_button)
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
            shown = 0
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
                if self._projects_only and not metadata.get('project_id'):
                    continue
                shown += 1
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
                title_label = Gtk.Label(label=title, xalign=0)
                title_label.add_css_class('heading')
                box.append(title_label)
                title_entry = Gtk.Entry(text=title)
                title_entry.set_hexpand(True)
                title_entry.set_visible(False)
                box.append(title_entry)
                box.append(Gtk.Label(label=activity, xalign=0))
                mountpoint = str(metadata.get('mountpoint') or '/')
                if mountpoint != '/':
                    volume = Gtk.Label(
                        label=_('External volume: %s') % mountpoint, xalign=0)
                    volume.add_css_class('dim-label')
                    volume.set_tooltip_text(
                        _('This entry is stored on an external volume'))
                    box.append(volume)
                keep = Gtk.CheckButton(label=_('Keep'))
                keep.set_active(str(metadata.get('keep', '0')).lower()
                                in ('1', 'true'))
                keep.set_tooltip_text(_('Keep this entry in the Journal'))
                keep.connect('toggled', self._keep_toggled, uid, metadata)
                box.append(keep)
                edit = Gtk.Button(label=_('Edit title'))
                edit.set_tooltip_text(_('Change this Journal entry title'))
                edit.connect('clicked', self._edit_title, edit, title_label,
                             title_entry, metadata)
                title_entry.connect('activate', self._finish_title, edit,
                                    title_label, title_entry, metadata)
                box.append(edit)
                delete = Gtk.Button(label=_('Delete'))
                delete.set_tooltip_text(_('Delete this Journal entry'))
                delete.connect('clicked', self._delete_clicked, uid)
                box.append(delete)
                project_id = str(metadata.get('project_id') or '')
                project_label = (_('Project: %s') % project_id
                                 if project_id else _('Project'))
                project = Gtk.Button(label=project_label)
                project.set_tooltip_text(_('Assign this entry to a project'))
                project.connect('clicked', self._project_clicked, metadata,
                                project)
                box.append(project)
                row.set_child(box)
                # Make keyboard traversal explicit in GTK4. ListBox otherwise
                # only guarantees pointer activation for rows whose child
                # hierarchy happens to be focusable.
                row.set_focusable(True)
                row.set_activatable(True)
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
            self._empty.set_visible(shown == 0)
            if self._projects_only and shown == 0:
                self._empty.set_text(_('No Journal entries are assigned to a project'))
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

    def _keep_toggled(self, button, uid, metadata):
        try:
            updated = editable_changes(
                metadata, {'keep': '1' if button.get_active() else '0'})
            write_metadata(
                updated,
                lambda *args: self._result_status.set_text(
                    _('Journal entry updated')),
                lambda error, *args: self._result_status.set_text(
                    _('Could not update Journal entry: %s') % error))
            metadata.update(updated)
        except (OSError, ValueError, TypeError) as error:
            button.set_active(not button.get_active())
            self._result_status.set_text(
                _('Could not update Journal entry: %s') % error)

    def _edit_title(self, _button, edit, title_label, title_entry, metadata):
        editing = title_entry.get_visible()
        if editing:
            self._finish_title(edit, edit, title_label, title_entry, metadata)
            return
        title_entry.set_text(str(metadata.get('title') or ''))
        title_label.set_visible(False)
        title_entry.set_visible(True)
        title_entry.grab_focus()
        title_entry.select_region(0, -1)
        edit.set_label(_('Save title'))

    def _finish_title(self, _entry, edit, title_label, title_entry, metadata):
        try:
            updated = editable_changes(
                metadata, {'title': title_entry.get_text()})
            write_metadata(
                updated,
                lambda *args: self._result_status.set_text(
                    _('Journal title updated')),
                lambda error, *args: self._result_status.set_text(
                    _('Could not update Journal title: %s') % error))
            metadata.update(updated)
            title_label.set_text(metadata['title'])
            title_label.set_visible(True)
            title_entry.set_visible(False)
            edit.set_label(_('Edit title'))
        except (OSError, ValueError, TypeError) as error:
            self._result_status.set_text(
                _('Could not update Journal title: %s') % error)

    def _delete_clicked(self, button, uid):
        # Require a deliberate second activation for this destructive action.
        if not getattr(button, '_delete_armed', False):
            button._delete_armed = True
            button.set_label(_('Confirm delete'))
            self._result_status.set_text(_('Activate Delete again to confirm'))
            GLib.timeout_add_seconds(5, self._reset_delete, button)
            return
        try:
            model.delete(str(uid))
        except (OSError, ValueError, TypeError) as error:
            self._result_status.set_text(
                _('Could not delete Journal entry: %s') % error)
            self._reset_delete(button)
            return
        self._result_status.set_text(_('Journal entry deleted'))
        self._refresh()

    @staticmethod
    def _reset_delete(button):
        button._delete_armed = False
        button.set_label(_('Delete'))
        return GLib.SOURCE_REMOVE

    def _project_clicked(self, _button, metadata, project_button):
        from jarabe.journal.objectchooser import ObjectChooser
        parent = self.get_root()
        chooser = ObjectChooser(parent=parent)
        chooser.connect('response', self._project_response, metadata,
                        project_button)
        chooser.present()

    def _project_response(self, chooser, response, metadata, project_button):
        if response != Gtk.ResponseType.ACCEPT:
            chooser.close()
            return
        project_id = chooser.get_selected_object_id()
        chooser.close()
        if not project_id:
            return
        try:
            updated = editable_changes(metadata, {'project_id': project_id})
            def applied(*args):
                metadata.update(updated)
                project_button.set_label(_('Project: %s') % project_id)
                self._result_status.set_text(_('Journal project updated'))

            def failed(error, *args):
                self._result_status.set_text(
                    _('Could not update Journal project: %s') % error)

            write_metadata(
                updated,
                applied, failed)
        except (OSError, ValueError, TypeError) as error:
            self._result_status.set_text(
                _('Could not update Journal project: %s') % error)

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

    def _projects_toggled(self, button):
        self._projects_only = button.get_active()
        GLib.idle_add(self._refresh)

    def get_projects_view_active(self): return self._projects_only
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
