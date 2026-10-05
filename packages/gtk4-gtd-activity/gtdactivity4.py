"""Native GTK4 Get Things Done task list Activity.

Tasks are stored as a small JSON Journal object.  This keeps the Activity
independent of datastore internals while making the useful offline workflow
survive a normal Sugar stop/resume cycle.
"""

import json
from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class GTDActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("Get Things Done"); self._build()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        root.set_margin_top(26); root.set_margin_bottom(26); root.set_margin_start(30); root.set_margin_end(30)
        root.set_hexpand(True); root.set_vexpand(True)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Task list"])
        heading = Gtk.Label(label="Get Things Done", xalign=0); heading.add_css_class("title-1"); root.append(heading)
        entry_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        entry_row.set_hexpand(True)
        self.entry = Gtk.Entry(); self.entry.set_placeholder_text("New task"); self.entry.set_hexpand(True); self.entry.update_property([Gtk.AccessibleProperty.LABEL], ["New task"]); self.entry.connect("activate", self._add); entry_row.append(self.entry)
        add = Gtk.Button(label="Add task"); add.connect("clicked", self._add); entry_row.append(add); root.append(entry_row)
        tasks_frame = Gtk.Frame(label="Tasks")
        tasks_frame.set_hexpand(True); tasks_frame.set_vexpand(True)
        self.tasks = Gtk.ListBox(); self.tasks.set_vexpand(True); self.tasks.set_hexpand(True)
        empty = Gtk.Label(label="No tasks yet. Add one above.", wrap=True)
        empty.add_css_class("empty-state")
        empty.set_margin_top(24); empty.set_margin_bottom(24)
        empty.set_margin_start(16); empty.set_margin_end(16)
        self.tasks.set_placeholder(empty)
        self.tasks.update_property([Gtk.AccessibleProperty.LABEL], ["Tasks"])
        tasks_frame.set_child(self.tasks); root.append(tasks_frame)
        self.summary = Gtk.Label(label="0 tasks", xalign=0); self.summary.add_css_class("dim-label"); root.append(self.summary)
        self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"frame { border: 2px solid #8aa8b8; border-radius: 8px; padding: 8px; } entry { min-height: 44px; } label.empty-state { background: #f1f5f7; border-radius: 12px; padding: 18px 24px; color: #52636b; } listboxrow { padding: 6px; } button { min-height: 42px; border-radius: 19px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _add(self, _widget):
        text = self.entry.get_text().strip()
        if not text: return
        self._append_task(text)
        self.entry.set_text("")
        self._update_summary()

    def _append_task(self, text, done=False):
        row = Gtk.ListBoxRow()
        row.set_activatable(False)
        content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        check = Gtk.CheckButton(label=text)
        check.set_hexpand(True)
        check.set_halign(Gtk.Align.START)
        check.set_active(done)
        check.update_property([Gtk.AccessibleProperty.LABEL], [text])
        check.connect("toggled", self._update_summary)
        content.append(check)
        for label, tooltip, delta in (("Move up", "Move task up", -1), ("Move down", "Move task down", 1)):
            move = Gtk.Button(label=label)
            move.set_tooltip_text(tooltip)
            move.update_property([Gtk.AccessibleProperty.LABEL], [f"{tooltip}: {text}"])
            move.connect("clicked", self._move_row, row, delta)
            content.append(move)
        remove = Gtk.Button(label="Remove task")
        remove.set_tooltip_text("Remove task")
        remove.update_property([Gtk.AccessibleProperty.LABEL], [f"Remove task: {text}"])
        remove.connect("clicked", self._remove_row, row)
        content.append(remove)
        row.task_check = check
        row.set_child(content)
        self.tasks.append(row)

    def _remove_row(self, _button, row):
        self._replace_rows([item for item in self._task_rows() if item is not row])
        self._update_summary()

    def _move_row(self, _button, row, delta):
        index = row.get_index()
        target = index + delta
        if index < 0 or target < 0 or self.tasks.get_row_at_index(target) is None:
            return
        rows = list(self._task_rows())
        rows[index], rows[target] = rows[target], rows[index]
        self._replace_rows(rows)
        self._update_summary()

    def _replace_rows(self, rows):
        tasks = [
            (row.task_check.get_label(), row.task_check.get_active())
            for row in rows
        ]
        for existing in list(self._task_rows()):
            self.tasks.remove(existing)
        for text, done in tasks:
            self._append_task(text, done)

    def _task_rows(self):
        """Yield real ListBoxRow children without treating the placeholder as a task."""
        index = 0
        while True:
            row = self.tasks.get_row_at_index(index)
            if row is None:
                return
            yield row
            index += 1

    def _update_summary(self, *_args):
        rows = [row.task_check for row in self._task_rows()]
        done = sum(button.get_active() for button in rows)
        self.summary.set_text(f"{len(rows)} tasks · {done} complete")

    def read_file(self, file_path):
        """Restore task text and completion state from a Journal object."""
        try:
            payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
            tasks = payload.get("tasks", []) if isinstance(payload, dict) else []
            if not isinstance(tasks, list):
                raise ValueError("tasks must be a list")
        except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
            tasks = []
        for row in list(self._task_rows()):
            self.tasks.remove(row)
        for task in tasks:
            if not isinstance(task, dict):
                continue
            text = str(task.get("text", "")).strip()
            if not text:
                continue
            self._append_task(text, bool(task.get("done", False)))
        self._update_summary()

    def write_file(self, file_path):
        """Write task text and completion state as a Journal object."""
        tasks = []
        for row in self._task_rows():
            check = row.task_check
            tasks.append({"text": check.get_label(), "done": check.get_active()})
        Path(file_path).write_text(
            json.dumps({"tasks": tasks}, sort_keys=True) + "\n", encoding="utf-8"
        )
