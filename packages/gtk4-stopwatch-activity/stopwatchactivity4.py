"""Native GTK4 Stopwatch Activity with Journal resume support.

Like GTK3 Stopwatch, several named stopwatches can run side by side and each
records marks (laps).  Time comes from the monotonic clock, so a busy main
loop never makes a stopwatch run slow.

Journal payload history (append-only):

* v1: ``{"elapsed": tenths}`` for a single stopwatch.
* v2 (2026-10-02): adds ``"version": 2`` and ``"watches"`` with names,
  milliseconds and marks, and keeps ``"elapsed"`` as the first stopwatch's
  tenths so v1 readers and the guest probe still understand it.

Resumed stopwatches are paused, as before.  Collaboration is not ported.
"""

import json
import time
from pathlib import Path

from gi.repository import Gdk, GLib, Gtk
from sugar4.activity import SimpleActivity


MAX_WATCHES = 6
MAX_MARKS = 50


def format_tenths(tenths):
    return f"{tenths // 600}:{(tenths // 10) % 60:02d}.{tenths % 10}"


class Watch:
    def __init__(self, name, elapsed_ms=0, marks=()):
        self.name = name
        self.base_ms = max(0, int(elapsed_ms))
        self.started = None
        self.marks = [max(0, int(m)) for m in marks][:MAX_MARKS]

    @property
    def running(self):
        return self.started is not None

    def elapsed_ms(self):
        if self.started is None:
            return self.base_ms
        return self.base_ms + int((time.monotonic() - self.started) * 1000)

    def start(self):
        if self.started is None:
            self.started = time.monotonic()

    def pause(self):
        self.base_ms = self.elapsed_ms()
        self.started = None

    def reset(self):
        self.base_ms, self.started, self.marks = 0, None, []

    def mark(self):
        if len(self.marks) < MAX_MARKS:
            self.marks.append(self.elapsed_ms())

    def to_json(self):
        return {"name": self.name, "elapsed_ms": self.elapsed_ms(), "marks": list(self.marks)}


class StopwatchActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Stopwatch")
        self.watches = []
        self._rows = []
        self._timer = None
        self._build()
        self._add_watch()
        self.display.set_text("00:00.0")

    # -- compatibility with the v1 single-stopwatch attributes ------------

    @property
    def elapsed(self):
        return self.watches[0].elapsed_ms() // 100 if self.watches else 0

    @property
    def running(self):
        return bool(self.watches) and self.watches[0].running

    # -- interface -----------------------------------------------------

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        root.set_margin_top(32); root.set_margin_bottom(32); root.set_margin_start(32); root.set_margin_end(32)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Stopwatch"])
        title = Gtk.Label(label="Stopwatch", xalign=0); title.add_css_class("title-1"); root.append(title)
        self.list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        scroll = Gtk.ScrolledWindow(); scroll.set_child(self.list); scroll.set_vexpand(True)
        root.append(scroll)
        self.add_button = Gtk.Button(label="Add stopwatch")
        self.add_button.set_tooltip_text("Add another stopwatch (up to %d)" % MAX_WATCHES)
        self.add_button.update_property([Gtk.AccessibleProperty.LABEL], ["Add stopwatch"])
        self.add_button.connect("clicked", lambda _b: self._add_watch())
        root.append(self.add_button)
        self.set_canvas(root)
        provider = Gtk.CssProvider()
        provider.load_from_data(b"button { min-height: 44px; border-radius: 19px; } .stopwatch-time { font-size: 28pt; font-feature-settings: 'tnum'; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _add_watch(self, watch=None):
        if len(self.watches) >= MAX_WATCHES:
            return
        watch = watch or Watch("Stopwatch %d" % (len(self.watches) + 1))
        self.watches.append(watch)
        row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        name = Gtk.Entry(text=watch.name)
        name.update_property([Gtk.AccessibleProperty.LABEL], ["Stopwatch name"])
        name.connect("changed", lambda entry, w=watch: setattr(w, "name", entry.get_text()))
        top.append(name)
        time_label = Gtk.Label(label=format_tenths(watch.elapsed_ms() // 100))
        time_label.add_css_class("stopwatch-time")
        time_label.update_property([Gtk.AccessibleProperty.LABEL], ["Elapsed time"])
        time_label.set_hexpand(True)
        top.append(time_label)
        row.append(top)
        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        toggle = Gtk.Button(label="Start")
        toggle.connect("clicked", lambda _b, w=watch: self._toggle(w))
        mark = Gtk.Button(label="Mark")
        mark.set_tooltip_text("Record the current time as a mark")
        mark.connect("clicked", lambda _b, w=watch: self._mark(w))
        reset = Gtk.Button(label="Reset")
        reset.connect("clicked", lambda _b, w=watch: self._reset(w))
        for button in (toggle, mark, reset):
            controls.append(button)
        row.append(controls)
        marks = Gtk.Label(xalign=0, wrap=True)
        marks.add_css_class("dim-label")
        marks.update_property([Gtk.AccessibleProperty.LABEL], ["Marks"])
        row.append(marks)
        self.list.append(row)
        self._rows.append({"watch": watch, "time": time_label, "toggle": toggle, "marks": marks})
        if len(self._rows) == 1:
            # v1 attribute names, kept for the guest probe and older tooling.
            self.display, self.toggle = time_label, toggle
        self.add_button.set_sensitive(len(self.watches) < MAX_WATCHES)
        self._refresh_row(self._rows[-1])

    def _row(self, watch):
        return next(row for row in self._rows if row["watch"] is watch)

    def _refresh_row(self, row):
        watch = row["watch"]
        row["time"].set_text(format_tenths(watch.elapsed_ms() // 100))
        row["toggle"].set_label("Pause" if watch.running else "Start")
        if watch.marks:
            recent = watch.marks[-5:]
            first = len(watch.marks) - len(recent) + 1
            row["marks"].set_text("Marks: " + "  ".join(
                "%d) %s" % (first + i, format_tenths(m // 100)) for i, m in enumerate(recent)))
        else:
            row["marks"].set_text("")

    def _toggle(self, watch):
        if watch.running:
            watch.pause()
        else:
            watch.start()
            if self._timer is None:
                self._timer = GLib.timeout_add(100, self._tick)
        self._refresh_row(self._row(watch))

    def _mark(self, watch):
        watch.mark()
        self._refresh_row(self._row(watch))

    def _reset(self, watch):
        watch.reset()
        self._refresh_row(self._row(watch))

    def _tick(self):
        running = False
        for row in self._rows:
            if row["watch"].running:
                running = True
                self._refresh_row(row)
        if not running:
            self._timer = None
            return GLib.SOURCE_REMOVE
        return GLib.SOURCE_CONTINUE

    def _replace_watches(self, watches):
        while (child := self.list.get_first_child()) is not None:
            self.list.remove(child)
        self.watches, self._rows = [], []
        for watch in watches[:MAX_WATCHES] or [Watch("Stopwatch 1")]:
            self._add_watch(watch)

    # -- Journal -------------------------------------------------------

    def read_file(self, file_path):
        """Restore stopwatches (paused) from a v1 or v2 Journal object."""
        watches = []
        try:
            state = json.loads(Path(file_path).read_text(encoding="utf-8"))
            if not isinstance(state, dict):
                raise ValueError("state must be an object")
            stored = state.get("watches")
            if isinstance(stored, list):
                for item in stored:
                    if not isinstance(item, dict):
                        continue
                    marks = item.get("marks", [])
                    marks = [m for m in marks if isinstance(m, int)] if isinstance(marks, list) else []
                    watches.append(Watch(str(item.get("name") or "Stopwatch %d" % (len(watches) + 1)),
                                         int(item.get("elapsed_ms", 0)), marks))
            if not watches:
                watches = [Watch("Stopwatch 1", max(0, int(state.get("elapsed", 0))) * 100)]
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            watches = [Watch("Stopwatch 1")]
        self._replace_watches(watches)

    def write_file(self, file_path):
        """Save every stopwatch; ``elapsed`` keeps the v1 meaning."""
        watches = [watch.to_json() for watch in self.watches]
        state = {"elapsed": watches[0]["elapsed_ms"] // 100 if watches else 0,
                 "version": 2, "watches": watches}
        Path(file_path).write_text(json.dumps(state, sort_keys=True) + "\n", encoding="utf-8")
