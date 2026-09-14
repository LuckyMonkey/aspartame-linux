# Copyright (C) 2006-2007, Eduardo Silva <edsiper@gmail.com>
# Copyright (C) 2009 Simon Schampijer
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import time
import logging
from gettext import gettext as _

import re

import gi
gi.require_version('Gdk', '4.0')
gi.require_version('Gtk', '4.0')
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Gio
from gi.repository import Gdk
from gi.repository import Gtk


from sugar4.activity import activity
from sugar4.activity.widgets import ActivityToolbarButton
from sugar4 import env
from sugar4.graphics import iconentry
from sugar4.graphics.toolbutton import ToolButton
from sugar4.graphics.toggletoolbutton import ToggleToolButton
from sugar4.graphics.palette import Palette
from sugar4.graphics.alert import NotifyAlert
from logcollect import LogCollect
from sugar4.graphics.toolbarbox import ToolbarBox
from sugar4.graphics.toolbarbox import ToolbarButton
from sugar4.activity.widgets import CopyButton, StopButton
from sugar4.datastore import datastore


_AUTOSEARCH_TIMEOUT = 1000


# Should be builtin to sugar.graphics.alert.NotifyAlert...
def _notify_response_cb(notify, response, activity):
    activity.remove_alert(notify)


class MultiLogView(Gtk.Paned):
    """GTK4 log browser using ListBox instead of removed GTK3 tree widgets."""

    def __init__(self, paths, extra_files):
        Gtk.Paned.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)

        self.paths = paths
        self.extra_files = extra_files
        self._gio_monitors = []
        self._monitored_paths = set()

        self.active_log = None
        self.logs = {}
        self.search_text = ''
        self._rows = {}
        self._row_paths = {}

        self._build_log_list()
        self._build_textview()
        self._configure_watcher()
        self._find_logs()

    def _build_log_list(self):
        self._listbox = Gtk.ListBox()
        self._listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self._listbox.set_activate_on_single_click(True)
        self._listbox.connect('row-selected', self._row_selected_cb)

        self.list_scroll = Gtk.ScrolledWindow()
        self.list_scroll.set_policy(Gtk.PolicyType.AUTOMATIC,
                                    Gtk.PolicyType.AUTOMATIC)
        self.list_scroll.set_child(self._listbox)
        self.list_scroll.set_size_request(300, -1)
        self.set_start_child(self.list_scroll)

    def _build_textview(self):
        self._textview = Gtk.TextView()
        self._textview.set_wrap_mode(Gtk.WrapMode.NONE)
        self._textview.set_monospace(True)
        self._textview.set_editable(False)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_child(self._textview)
        self.set_end_child(scroll)

    def _sort_key(self, path):
        name = os.path.basename(path).lower()
        match = re.match(r'(.*)-(\d+)\.log', name, re.IGNORECASE)
        if match:
            return (0, match.group(1), int(match.group(2)), name)
        if name.endswith('.log'):
            return (1, name)
        return (2, name)

    def _refresh_rows(self):
        for row in list(self._rows.values()):
            self._listbox.remove(row)
        self._rows.clear()
        self._row_paths.clear()

        for path in sorted(self.logs, key=self._sort_key):
            row = Gtk.ListBoxRow()
            label = Gtk.Label(label=path)
            label.set_xalign(0.0)
            label.set_hexpand(True)
            label.set_margin_start(8)
            label.set_margin_end(8)
            label.set_margin_top(4)
            label.set_margin_bottom(4)
            label.set_tooltip_text(path)
            row.set_child(label)
            self._listbox.append(row)
            self._rows[path] = row
            self._row_paths[row] = path

        if self.active_log is not None:
            row = self._rows.get(self.active_log.logfile)
            if row is not None:
                self._listbox.select_row(row)

    def _row_selected_cb(self, listbox, row):
        if row is not None:
            self._show_log(self._row_paths.get(row))

    def _configure_watcher(self):
        for path in self.paths + self.extra_files:
            self._watch_path(path)

    def _watch_path(self, path):
        path = os.path.abspath(os.path.expanduser(path))
        if path in self._monitored_paths:
            return

        if os.path.isdir(path):
            self._create_gio_monitor(path, directory=True)
            for root, directories, _files in os.walk(path):
                for directory in directories:
                    self._create_gio_monitor(
                        os.path.join(root, directory), directory=True)
        elif os.path.isfile(path):
            self._create_gio_monitor(path, directory=False)

    def _create_gio_monitor(self, path, directory):
        path = os.path.abspath(path)
        if path in self._monitored_paths:
            return

        try:
            file_object = Gio.File.new_for_path(path)
            if directory:
                monitor = file_object.monitor_directory(
                    Gio.FileMonitorFlags.NONE, None)
            else:
                monitor = file_object.monitor_file(
                    Gio.FileMonitorFlags.NONE, None)
        except GLib.Error:
            logging.debug(_("Unable to monitor '%s'."), path, exc_info=True)
            return

        monitor.connect('changed', self._log_file_changed_cb)
        self._gio_monitors.append(monitor)
        self._monitored_paths.add(path)

    def _log_file_changed_cb(self, monitor, log_file, other_file, event):
        filepath = log_file.get_path()
        if not filepath:
            return
        filepath = os.path.abspath(filepath)

        if event == Gio.FileMonitorEvent.CHANGED:
            if filepath in self.logs:
                log = self.logs[filepath]
                log.update()
                if self.active_log == log:
                    self._textview.scroll_to_mark(
                        log.get_insert(), 0, use_align=False,
                        xalign=0.5, yalign=0.5)
        elif event == Gio.FileMonitorEvent.DELETED:
            self._remove_log_file(filepath)
        elif event == Gio.FileMonitorEvent.CREATED:
            if os.path.isdir(filepath):
                self._watch_path(filepath)
                self._find_logs_in(filepath)
            else:
                self._add_log_file(filepath)

    def _find_logs_in(self, directory):
        try:
            entries = os.listdir(directory)
        except OSError:
            logging.debug(_("Unable to inspect '%s'."), directory,
                          exc_info=True)
            return

        for name in entries:
            path = os.path.join(directory, name)
            if os.path.isdir(path):
                self._watch_path(path)
                self._find_logs_in(path)
            else:
                self._add_log_file(path)

    def _show_log(self, logfile):
        if not logfile or logfile not in self.logs:
            return

        log = self.logs[logfile]
        self._textview.set_buffer(log)
        self._textview.scroll_to_mark(
            log.get_insert(), 0, use_align=False, xalign=0.5, yalign=0.5)
        self.active_log = log

        row = self._rows.get(logfile)
        if row is not None and self._listbox.get_selected_row() is not row:
            self._listbox.select_row(row)

    def _find_logs(self):
        for path in self.paths + self.extra_files:
            path = os.path.abspath(os.path.expanduser(path))
            if os.path.isdir(path):
                self._find_logs_in(path)
            elif os.path.isfile(path):
                self._add_log_file(path)

    def _add_log_file(self, path):
        path = os.path.abspath(os.path.expanduser(path))
        if os.path.isdir(path):
            self._watch_path(path)
            self._find_logs_in(path)
            return False

        if not os.path.isfile(path) or not os.access(path, os.R_OK):
            logging.debug(_("Unable to read file '%s'."), path)
            return False

        if path not in self.logs:
            log = LogBuffer(path, None)
            self.logs[path] = log
        else:
            log = self.logs[path]
            log.update()

        self._refresh_rows()
        if self.active_log is None:
            self._show_log(path)
        elif self.active_log == log and log._written > 0:
            self._textview.scroll_to_mark(
                log.get_insert(), 0, use_align=False, xalign=0.5, yalign=0.5)

        return True

    def _remove_log_file(self, logfile):
        log = self.logs.pop(logfile, None)
        if log is None:
            return

        was_active = self.active_log is log
        if was_active:
            self.active_log = None
            self._textview.set_buffer(Gtk.TextBuffer())

        self._refresh_rows()
        if was_active and self.logs:
            self._show_log(sorted(self.logs, key=self._sort_key)[0])

    def set_search_text(self, text):
        self.search_text = text or ''

        buffer = self._textview.get_buffer()
        start, end = buffer.get_bounds()
        buffer.remove_tag_by_name('search-hilite', start, end)
        buffer.remove_tag_by_name('search-select', start, end)

        if not self.search_text:
            return

        text_iter = buffer.get_start_iter()
        while True:
            next_found = text_iter.forward_search(self.search_text, 0, None)
            if next_found is None:
                break
            start, end = next_found
            buffer.apply_tag_by_name('search-hilite', start, end)
            text_iter = end

        if self.get_next_result('current'):
            self.search_next('current')
        elif self.get_next_result('backward'):
            self.search_next('backward')

    def get_next_result(self, direction):
        buffer = self._textview.get_buffer()
        if not self.search_text:
            return None

        if direction == 'forward':
            text_iter = buffer.get_iter_at_mark(buffer.get_insert())
            text_iter.forward_char()
        else:
            text_iter = buffer.get_iter_at_mark(buffer.get_insert())

        if direction == 'backward':
            return text_iter.backward_search(self.search_text, 0, None)
        return text_iter.forward_search(self.search_text, 0, None)

    def search_next(self, direction):
        next_found = self.get_next_result(direction)
        if next_found:
            buffer = self._textview.get_buffer()
            start, end = buffer.get_bounds()
            buffer.remove_tag_by_name('search-select', start, end)

            start, end = next_found
            buffer.apply_tag_by_name('search-select', start, end)
            buffer.place_cursor(start)

            self._textview.scroll_to_iter(
                start, 0.1, use_align=False, xalign=0.5, yalign=0.5)
            self._textview.scroll_to_iter(
                end, 0.1, use_align=False, xalign=0.5, yalign=0.5)



class LogBuffer(Gtk.TextBuffer):

    def __init__(self, logfile, iterator):
        GObject.GObject.__init__(self)

        _tagtable = self.get_tag_table()
        hilite_tag = Gtk.TextTag.new('search-hilite')
        hilite_tag.props.background = '#FFFFB0'
        _tagtable.add(hilite_tag)
        select_tag = Gtk.TextTag.new('search-select')
        select_tag.props.background = '#B0B0FF'
        _tagtable.add(select_tag)

        self.logfile = logfile
        self._pos = 0
        self.iter = iterator
        self.update()

    def append_formatted_text(self, text):
        # Remove ANSI escape codes.
        # todo- Handle a subset of them.
        strip_ansi = re.compile(r'\033\[[\d;]*m')
        text = strip_ansi.sub('', text)
        self.insert(self.get_end_iter(), text)

    def update(self):
        try:
            f = open(self.logfile, 'r')
            init_pos = self._pos

            f.seek(self._pos)
            self.append_formatted_text(f.read())
            self._pos = f.tell()
            f.close()

            self._written = (self._pos - init_pos)
        except BaseException:
            self.insert(self.get_end_iter(),
                        _("Error: Can't open file '%s'\n") % self.logfile)
            self._written = 0


class LogActivity(activity.Activity):
    def __init__(self, handle):
        activity.Activity.__init__(self, handle)

        self._autosearch_timer = None

        # Paths to watch: ~/.sugar/someuser/logs, /var/log
        paths = []
        paths.append(env.get_profile_path('logs'))
        paths.append('/var/log')

        # Additional misc files.
        ext_files = []
        ext_files.append(os.path.expanduser('~/.bash_history'))

        self.viewer = MultiLogView(paths, ext_files)
        self.set_canvas(self.viewer)
        self.viewer.grab_focus()

        self._build_toolbox()

        # Get Sugar's clipboard
        self.clipboard = self.get_clipboard()
        self.set_visible(True)

        self._configure_cb(None)

    def _build_toolbox(self):
        toolbar_box = ToolbarBox()

        self.max_participants = 1

        activity_button = ActivityToolbarButton(self)
        activity_toolbar = activity_button.page
        activity_toolbar.add_css_class('toolbar')

        self._toolbar = toolbar_box.get_toolbar()
        self._toolbar.add_css_class('toolbar')
        self._toolbar.append(activity_button)

        self._secondary_toolbar = Gtk.Box()
        self._secondary_toolbar.add_css_class('toolbar')
        self._secondary_toolbar_button = ToolbarButton(
            page=self._secondary_toolbar,
            icon_name='system-search')
        self._secondary_toolbar.set_visible(True)
        self._toolbar.append(self._secondary_toolbar_button)
        self._secondary_toolbar_button.set_visible(False)

        show_list = ToggleToolButton('view-list')
        show_list.set_active(True)
        show_list.set_tooltip(_('Show list of files'))
        show_list.connect('toggled', self._list_toggled_cb)
        self._toolbar.append(show_list)
        show_list.set_visible(True)

        copy = CopyButton()
        copy.connect('clicked', self.__copy_clicked_cb)
        self._toolbar.append(copy)

        wrap_btn = ToggleToolButton("format-wrap")
        wrap_btn.set_tooltip(_('Word Wrap'))
        wrap_btn.connect('clicked', self._wrap_cb)
        self._toolbar.append(wrap_btn)

        self.search_entry = iconentry.IconEntry()
        self.search_entry.set_size_request(250, -1)
        self.search_entry.set_icon_from_name(
            iconentry.ICON_ENTRY_PRIMARY, 'entry-search')
        self.search_entry.add_clear_button()
        self.search_entry.connect('activate', self._search_entry_activate_cb)
        self.search_entry.connect('changed', self._search_entry_changed_cb)
        self._toolbar.append(self.search_entry)

        self._search_prev = ToolButton('go-previous-paired')
        self._search_prev.set_tooltip(_('Previous'))
        self._search_prev.connect('clicked', self._search_prev_cb)
        self._toolbar.append(self._search_prev)

        self._search_next = ToolButton('go-next-paired')
        self._search_next.set_tooltip(_('Next'))
        self._search_next.connect('clicked', self._search_next_cb)
        self._toolbar.append(self._search_next)

        self._update_search_buttons()

        self.collector_palette = CollectorPalette(self)
        collector_btn = ToolButton('log-export')
        collector_btn.set_palette(self.collector_palette)
        collector_btn.connect('clicked', self._logviewer_cb)
        collector_btn.set_visible(True)
        activity_toolbar.append(collector_btn)

        self._delete_btn = ToolButton('list-remove')
        self._delete_btn = ToolButton('list-remove', accelerator='<ctrl>d')
        self._delete_btn.set_tooltip(_('Delete Log File'))
        self._delete_btn.connect('clicked', self._delete_log_cb)
        self._toolbar.append(self._delete_btn)

        self._separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        self._separator.set_hexpand(True)
        self._toolbar.append(self._separator)

        self._stop_btn = StopButton(self)
        self._toolbar.append(self._stop_btn)

        self.set_toolbar_box(toolbar_box)

    def _configure_cb(self, event=None):
        for control in [self._stop_btn, self._separator, self._delete_btn]:
            if control.get_parent() == self._toolbar:
                self._toolbar.remove(control)

        if self.get_width() < self.get_height():
            self._secondary_toolbar_button.set_visible(True)
            self._secondary_toolbar_button.set_expanded(True)
            self._remove_controls(self._toolbar)
            self._add_controls(self._secondary_toolbar)
        else:
            self._secondary_toolbar_button.set_expanded(False)
            self._secondary_toolbar_button.set_visible(False)
            self._remove_controls(self._secondary_toolbar)
            self._add_controls(self._toolbar)

        for control in [self._delete_btn, self._separator, self._stop_btn]:
            if control.get_parent() != self._toolbar:
                parent = control.get_parent()
                if parent:
                    parent.remove(control)
                self._toolbar.append(control)

    def _remove_controls(self, toolbar):
        for control in [self.search_entry, self._search_prev,
                        self._search_next]:
            if control.get_parent() == toolbar:
                toolbar.remove(control)

    def _add_controls(self, toolbar):
        for control in [self.search_entry, self._search_prev,
                        self._search_next]:
            if control.get_parent() != toolbar:
                parent = control.get_parent()
                if parent:
                    parent.remove(control)
                toolbar.append(control)
                control.set_visible(True)

    def _list_toggled_cb(self, widget):
        if widget.get_active():
            self.viewer.list_scroll.set_visible(True)
        else:
            self.viewer.list_scroll.set_visible(False)

    def __copy_clicked_cb(self, button):
        if self.viewer.active_log:
            self.viewer.active_log.copy_clipboard(self.clipboard)

    def _wrap_cb(self, button):
        if button.get_active():
            self.viewer._textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        else:
            self.viewer._textview.set_wrap_mode(Gtk.WrapMode.NONE)

    def _search_entry_activate_cb(self, entry):
        if self._autosearch_timer:
            GLib.source_remove(self._autosearch_timer)
            self._autosearch_timer = None
        self.viewer.set_search_text(entry.props.text)
        self._update_search_buttons()

    def _search_entry_changed_cb(self, entry):
        if self._autosearch_timer:
            GLib.source_remove(self._autosearch_timer)
        self._autosearch_timer = GLib.timeout_add(_AUTOSEARCH_TIMEOUT,
                                                  self.__autosearch_cb)

    def __autosearch_cb(self):
        self._autosearch_timer = None
        self.search_entry.activate()
        return False

    def _search_prev_cb(self, button):
        self.viewer.search_next('backward')
        self._update_search_buttons()

    def _search_next_cb(self, button):
        self.viewer.search_next('forward')
        self._update_search_buttons()

    def _update_search_buttons(self,):
        if len(self.viewer.search_text) == 0:
            self._search_prev.props.sensitive = False
            self._search_next.props.sensitive = False
        else:
            prev_result = self.viewer.get_next_result('backward')
            next_result = self.viewer.get_next_result('forward')
            self._search_prev.props.sensitive = prev_result is not None
            self._search_next.props.sensitive = next_result is not None

    def _delete_log_cb(self, widget):
        if self.viewer.active_log:
            logfile = self.viewer.active_log.logfile
            try:
                os.remove(logfile)
            except OSError as err:
                notify = NotifyAlert()
                notify.props.title = _('Error')
                notify.props.msg = _('%(error)s when deleting %(file)s') % \
                    {'error': err.strerror, 'file': logfile}
                notify.connect('response', _notify_response_cb, self)
                self.add_alert(notify)

    def _logviewer_cb(self, widget):
        self.collector_palette.popup(True)


class CollectorPalette(Palette):
    def __init__(self, activity):
        Palette.__init__(self, _('Log Collector: Capture information'))

        self._activity = activity

        self._collector = LogCollect()

        trans = _('This captures information about the system\n'
                  'and running processes to a journal entry.\n'
                  'Use this to improve a problem report.')
        label = Gtk.Label(label=trans)

        send_button = Gtk.Button(label=_('Capture information'))
        send_button.connect('clicked', self._on_send_button_clicked_cb)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        label.set_vexpand(True)
        vbox.append(label)
        send_button.set_vexpand(True)
        vbox.append(send_button)

        self.set_content(vbox)

    def _on_send_button_clicked_cb(self, button):
        old_cursor = self._activity.get_cursor()
        self._activity.set_cursor(Gdk.Cursor.new_from_name("wait", None))

        identifier = str(int(time.time()))
        filename = '%s.zip' % identifier
        filepath = os.path.join(activity.get_activity_root(), filename)
        success = True
        # FIXME: subprocess or thread
        try:
            self._collector.write_logs(archive=filepath, logbytes=0)
        except BaseException:
            success = False

        self.popdown(True)

        if not success:
            title = _('Logs not captured')
            msg = _('The logs could not be captured.')

            notify = NotifyAlert()
            notify.props.title = title
            notify.props.msg = msg
            notify.connect('response', _notify_response_cb, self._activity)
            self._activity.add_alert(notify)

        jobject = datastore.create()
        metadata = {
            'title': _('log-%s') % filename,
            'title_set_by_user': '0',
            'suggested_filename': filename,
            'mime_type': 'application/zip',
        }
        for k, v in list(metadata.items()):
            jobject.metadata[k] = v
        jobject.file_path = filepath
        datastore.write(jobject)
        self._last_log = jobject.object_id
        jobject.destroy()
        activity.show_object_in_journal(self._last_log)
        os.remove(filepath)

        self._activity.set_cursor(old_cursor)
