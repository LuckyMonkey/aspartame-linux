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
        self.tasks.set_placeholder(Gtk.Label(label="No tasks yet. Add one above.", xalign=0))
        self.tasks.update_property([Gtk.AccessibleProperty.LABEL], ["Tasks"])
        tasks_frame.set_child(self.tasks); root.append(tasks_frame)
        self.summary = Gtk.Label(label="0 tasks", xalign=0); self.summary.add_css_class("dim-label"); root.append(self.summary)
        self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"frame { border: 2px solid #8aa8b8; border-radius: 8px; padding: 8px; } entry { min-height: 44px; } button { min-height: 42px; border-radius: 19px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _add(self, _widget):
        text = self.entry.get_text().strip()
        if not text: return
        check = Gtk.CheckButton(label=text); check.set_hexpand(True); check.set_halign(Gtk.Align.START); check.update_property([Gtk.AccessibleProperty.LABEL], [text]); check.connect("toggled", self._update_summary)
        self.tasks.append(Gtk.ListBoxRow(child=check)); self.entry.set_text(""); self._update_summary()

    def _update_summary(self, *_args):
        rows = [row.get_child() for row in self.tasks]
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
        for row in list(self.tasks):
            self.tasks.remove(row)
        for task in tasks:
            if not isinstance(task, dict):
                continue
            text = str(task.get("text", "")).strip()
            if not text:
                continue
            check = Gtk.CheckButton(label=text)
            check.set_hexpand(True)
            check.set_halign(Gtk.Align.START)
            check.set_active(bool(task.get("done", False)))
            check.update_property([Gtk.AccessibleProperty.LABEL], [text])
            check.connect("toggled", self._update_summary)
            self.tasks.append(Gtk.ListBoxRow(child=check))
        self._update_summary()

    def write_file(self, file_path):
        """Write task text and completion state as a Journal object."""
        tasks = []
        for row in self.tasks:
            check = row.get_child()
            tasks.append({"text": check.get_label(), "done": check.get_active()})
        Path(file_path).write_text(
            json.dumps({"tasks": tasks}, sort_keys=True) + "\n", encoding="utf-8"
        )
