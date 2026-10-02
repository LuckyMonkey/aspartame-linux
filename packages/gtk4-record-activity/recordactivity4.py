"""Native GTK4 Record Activity: photos, video, and audio through GStreamer.

The GTK3 Record keeps each capture as a separate Journal object and refers to
them from an XML index.  This port keeps the session self-contained instead:
the Activity's own Journal object is a small zip archive holding a JSON
manifest and the captured media, so stop/resume restores every capture without
a datastore round trip per file.

Capture runs as a plain GStreamer pipeline per recording.  Devices are found
with ``Gst.DeviceMonitor``; when no camera or microphone exists the matching
mode says so instead of pretending.  The pipeline source can be overridden for
headless tests and camera-less VMs with ``ASPARTAME_RECORD_VIDEO_SOURCE`` and
``ASPARTAME_RECORD_AUDIO_SOURCE`` (for example ``videotestsrc is-live=true``).
A live camera viewfinder, timers, and collaboration remain unported.
"""

import atexit
import json
import os
import shutil
import tempfile
import time
import zipfile
from pathlib import Path

import gi
from gi.repository import Gdk, GLib, Gtk
from sugar4.activity import SimpleActivity

try:
    gi.require_version("Gst", "1.0")
    from gi.repository import Gst
    Gst.init(None)
except (ValueError, ImportError):  # GStreamer introspection is not installed
    Gst = None


MANIFEST = "manifest.json"
MEDIA_DIR = "media/"
FORMAT_VERSION = 1
MAX_SECONDS = 600
# Fixed archive timestamps keep an unchanged session byte-identical on save.
ZIP_DATE = (1980, 1, 1, 0, 0, 0)

MODES = {
    "photo": {"label": "Photo", "device": "Video/Source", "suffix": ".png",
              "action": "Take photo", "encoder": "videoconvert ! pngenc snapshot=true"},
    "video": {"label": "Video", "device": "Video/Source", "suffix": ".webm",
              "action": "Start recording",
              "encoder": "videoconvert ! vp8enc deadline=1 ! webmmux"},
    "audio": {"label": "Audio", "device": "Audio/Source", "suffix": ".ogg",
              "action": "Start recording",
              "encoder": "audioconvert ! audioresample ! opusenc ! oggmux"},
}
SOURCE_ENV = {"Video/Source": "ASPARTAME_RECORD_VIDEO_SOURCE",
              "Audio/Source": "ASPARTAME_RECORD_AUDIO_SOURCE"}
DEFAULT_SOURCE = {"Video/Source": "v4l2src", "Audio/Source": "autoaudiosrc"}


def source_for(device_class):
    return os.environ.get(SOURCE_ENV[device_class]) or DEFAULT_SOURCE[device_class]


def pipeline_description(mode, source):
    """GStreamer launch line for ``mode``; the sink location is set separately."""
    return "%s ! %s ! filesink name=sink" % (source, MODES[mode]["encoder"])


def available_device_classes():
    """Device classes with real hardware, plus any explicitly overridden source."""
    found = {klass for klass, env in SOURCE_ENV.items() if os.environ.get(env)}
    if Gst is None:
        return found
    monitor = Gst.DeviceMonitor()
    for klass in SOURCE_ENV:
        monitor.add_filter(klass, None)
    if monitor.start():
        try:
            for device in monitor.get_devices() or []:
                for klass in SOURCE_ENV:
                    if device.has_classes(klass):
                        found.add(klass)
        finally:
            monitor.stop()
    return found


class ClipStore:
    """Captured media on disk plus the manifest that describes it."""

    def __init__(self, directory):
        self.directory = Path(directory)
        self.clips = []

    def path(self, clip):
        return self.directory / clip["file"]

    def new_clip(self, kind):
        number = 1 + sum(1 for clip in self.clips if clip["kind"] == kind)
        stem = "%s-%d" % (kind, number)
        while any(clip["file"].startswith(stem + ".") for clip in self.clips):
            number += 1
            stem = "%s-%d" % (kind, number)
        return {"kind": kind, "title": "%s %d" % (MODES[kind]["label"], number),
                "file": stem + MODES[kind]["suffix"], "created": int(time.time())}

    def add(self, clip):
        self.clips.append(clip)

    def remove(self, index):
        clip = self.clips.pop(index)
        self.path(clip).unlink(missing_ok=True)

    def save(self, file_path):
        manifest = {"version": FORMAT_VERSION, "clips": self.clips}
        with zipfile.ZipFile(file_path, "w") as archive:
            info = zipfile.ZipInfo(MANIFEST, ZIP_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, json.dumps(manifest, sort_keys=True) + "\n")
            for clip in self.clips:
                # Media is already compressed; store it as-is.
                info = zipfile.ZipInfo(MEDIA_DIR + clip["file"], ZIP_DATE)
                archive.writestr(info, self.path(clip).read_bytes())

    def load(self, file_path):
        """Replace the clips with a saved session; ignore anything malformed."""
        restored = []
        try:
            with zipfile.ZipFile(file_path) as archive:
                manifest = json.loads(archive.read(MANIFEST).decode("utf-8"))
                if not isinstance(manifest, dict) or not isinstance(manifest.get("clips"), list):
                    raise ValueError("manifest has no clip list")
                names = set(archive.namelist())
                for clip in manifest["clips"]:
                    clip = self._valid_clip(clip, names)
                    if clip is None or any(kept["file"] == clip["file"] for kept in restored):
                        continue
                    data = archive.read(MEDIA_DIR + clip["file"])
                    (self.directory / clip["file"]).write_bytes(data)
                    restored.append(clip)
        except (OSError, ValueError, KeyError, zipfile.BadZipFile):
            return False
        kept = {clip["file"] for clip in restored}
        for clip in self.clips:
            if clip["file"] not in kept:
                self.path(clip).unlink(missing_ok=True)
        self.clips = restored
        return True

    @staticmethod
    def _valid_clip(clip, names):
        if not isinstance(clip, dict) or clip.get("kind") not in MODES:
            return None
        name = clip.get("file")
        # Only plain file names: a manifest must never write outside the store.
        if not isinstance(name, str) or Path(name).name != name or name.startswith("."):
            return None
        if not name.endswith(MODES[clip["kind"]]["suffix"]) or MEDIA_DIR + name not in names:
            return None
        try:
            created = int(clip.get("created", 0))
        except (TypeError, ValueError):
            created = 0
        return {"kind": clip["kind"], "title": str(clip.get("title") or name),
                "file": name, "created": created}


class Recorder:
    """One capture pipeline; reports completion through ``on_done(ok, error)``."""

    def __init__(self, mode, location, on_done):
        device = MODES[mode]["device"]
        self.pipeline = Gst.parse_launch(pipeline_description(mode, source_for(device)))
        self.pipeline.get_by_name("sink").set_property("location", str(location))
        self._on_done = on_done
        self._watch = None
        self._finished = False

    def start(self):
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        self._watch = bus.connect("message", self._message)
        if self.pipeline.set_state(Gst.State.PLAYING) == Gst.StateChangeReturn.FAILURE:
            self._finish(False, "The capture device could not be started.")

    def stop(self):
        """Ask the source to end the stream so the file is finalized cleanly."""
        if self._finished:
            return
        self.pipeline.send_event(Gst.Event.new_eos())
        GLib.timeout_add_seconds(5, self._force_stop)

    def cancel(self):
        self._finish(False, None)

    def _force_stop(self):
        self._finish(False, "Recording did not finish cleanly.")
        return GLib.SOURCE_REMOVE

    def _message(self, _bus, message):
        if message.type == Gst.MessageType.EOS:
            self._finish(True, None)
        elif message.type == Gst.MessageType.ERROR:
            error, _debug = message.parse_error()
            self._finish(False, error.message)

    def _finish(self, ok, error):
        if self._finished:
            return
        self._finished = True
        self.pipeline.set_state(Gst.State.NULL)
        bus = self.pipeline.get_bus()
        if self._watch is not None:
            bus.disconnect(self._watch)
            bus.remove_signal_watch()
        self._on_done(ok, error)


class RecordActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Record")
        directory = tempfile.mkdtemp(prefix="record4-")
        atexit.register(shutil.rmtree, directory, True)
        self.store = ClipStore(directory)
        self.mode = "photo"
        self.recorder = None
        self._pending = None
        self._started = 0
        self._tick = None
        self.devices = available_device_classes()
        self._build()
        self.connect("destroy", self._destroyed, directory)

    # -- interface -----------------------------------------------------

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        root.set_margin_top(28); root.set_margin_bottom(28)
        root.set_margin_start(32); root.set_margin_end(32)
        root.set_accessible_role(Gtk.AccessibleRole.GROUP)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Record photos, video, and audio"])

        title = Gtk.Label(label="Record", xalign=0)
        title.add_css_class("title-1")
        root.append(title)

        modes = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.mode_buttons = {}
        group = None
        for mode, spec in MODES.items():
            button = Gtk.ToggleButton(label=spec["label"])
            button.update_property([Gtk.AccessibleProperty.LABEL], ["%s mode" % spec["label"]])
            if group is not None:
                button.set_group(group)
            group = group or button
            button.connect("toggled", self._mode_toggled, mode)
            self.mode_buttons[mode] = button
            modes.append(button)
        root.append(modes)

        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.capture = Gtk.Button()
        self.capture.add_css_class("suggested-action")
        self.capture.connect("clicked", self._capture_clicked)
        actions.append(self.capture)
        self.remove = Gtk.Button(label="Remove")
        self.remove.update_property([Gtk.AccessibleProperty.LABEL], ["Remove selected recording"])
        self.remove.connect("clicked", self._remove_clicked)
        actions.append(self.remove)
        root.append(actions)

        self.status = Gtk.Label(xalign=0, wrap=True)
        self.status.update_property([Gtk.AccessibleProperty.LABEL], ["Record status"])
        root.append(self.status)
        # Device availability is a standing condition, kept apart from the
        # status line so it never hides what just happened.
        self.hint = Gtk.Label(xalign=0, wrap=True)
        self.hint.add_css_class("dim-label")
        root.append(self.hint)

        content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        content.set_vexpand(True)
        self.preview = Gtk.Stack()
        self.preview.set_hexpand(True)
        empty = Gtk.Label(label="Your photos, videos, and recordings appear here.")
        empty.add_css_class("dim-label")
        self.preview.add_named(empty, "empty")
        self.picture = Gtk.Picture(can_shrink=True)
        self.picture.update_property([Gtk.AccessibleProperty.LABEL], ["Selected photo"])
        self.preview.add_named(self.picture, "picture")
        self.video = Gtk.Video(autoplay=False)
        self.video.update_property([Gtk.AccessibleProperty.LABEL], ["Selected recording"])
        self.preview.add_named(self.video, "media")
        content.append(self.preview)

        self.gallery = Gtk.ListBox(selection_mode=Gtk.SelectionMode.SINGLE)
        self.gallery.update_property([Gtk.AccessibleProperty.LABEL], ["Recordings"])
        self.gallery.connect("row-selected", self._row_selected)
        scroll = Gtk.ScrolledWindow(); scroll.set_child(self.gallery)
        scroll.set_size_request(260, -1)
        content.append(scroll)
        root.append(content)

        self.set_canvas(root)
        self._install_css()
        self.mode_buttons["photo"].set_active(True)
        self._refresh_gallery()

    def _install_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(b"button { min-height: 44px; border-radius: 19px; } listboxrow { padding: 10px; }")
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _sync_controls(self):
        recording = self.recorder is not None
        spec = MODES[self.mode]
        available = Gst is not None and spec["device"] in self.devices
        if recording:
            self.capture.set_label("Stop recording")
        else:
            self.capture.set_label(spec["action"])
        self.capture.update_property([Gtk.AccessibleProperty.LABEL], [self.capture.get_label()])
        self.capture.set_sensitive(recording or available)
        for button in self.mode_buttons.values():
            button.set_sensitive(not recording)
        self.remove.set_sensitive(not recording and self.gallery.get_selected_row() is not None)
        if Gst is None:
            hint = "GStreamer is not installed, so nothing can be recorded."
        elif not available:
            what = "camera" if spec["device"] == "Video/Source" else "microphone"
            hint = "No %s was found. Connect one to record %s." % (what, spec["label"].lower())
        else:
            hint = ""
        self.hint.set_text(hint)
        self.hint.set_visible(bool(hint))

    def _mode_toggled(self, button, mode):
        if not button.get_active():
            return
        self.mode = mode
        self.status.set_text("%s mode." % MODES[mode]["label"])
        self._sync_controls()

    def _refresh_gallery(self, select=None):
        while (row := self.gallery.get_row_at_index(0)) is not None:
            self.gallery.remove(row)
        for index, clip in enumerate(self.store.clips):
            row = Gtk.ListBoxRow()
            row.clip_index = index
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            box.append(Gtk.Label(label=clip["title"], xalign=0))
            stamp = time.strftime("%Y-%m-%d %H:%M", time.localtime(clip["created"]))
            detail = Gtk.Label(label="%s · %s" % (MODES[clip["kind"]]["label"], stamp), xalign=0)
            detail.add_css_class("dim-label")
            box.append(detail)
            row.set_child(box)
            row.update_property([Gtk.AccessibleProperty.LABEL], [clip["title"]])
            self.gallery.append(row)
        if select is not None and (row := self.gallery.get_row_at_index(select)) is not None:
            self.gallery.select_row(row)
        else:
            self._show(None)
        self._sync_controls()

    def _row_selected(self, _gallery, row):
        self._show(None if row is None else self.store.clips[row.clip_index])
        self._sync_controls()

    def _show(self, clip):
        self.video.set_file(None)
        if clip is None:
            self.picture.set_filename(None)
            self.preview.set_visible_child_name("empty")
        elif clip["kind"] == "photo":
            self.picture.set_filename(str(self.store.path(clip)))
            self.preview.set_visible_child_name("picture")
        else:
            self.video.set_filename(str(self.store.path(clip)))
            self.preview.set_visible_child_name("media")

    # -- capture -------------------------------------------------------

    def _capture_clicked(self, _button):
        if self.recorder is not None:
            self.status.set_text("Finishing %s…" % self._pending["title"])
            self.capture.set_sensitive(False)
            self.recorder.stop()
            return
        clip = self.store.new_clip(self.mode)
        try:
            recorder = Recorder(self.mode, self.store.path(clip), self._capture_done)
        except GLib.Error as error:
            self.status.set_text("Unable to start %s: %s" % (MODES[self.mode]["label"].lower(), error.message))
            return
        self.recorder, self._pending = recorder, clip
        self._started = time.monotonic()
        if self.mode == "photo":
            self.status.set_text("Taking a photo…")
        else:
            self.status.set_text("Recording %s — 0:00" % clip["title"])
            self._tick = GLib.timeout_add_seconds(1, self._update_elapsed)
        self._sync_controls()
        recorder.start()

    def _update_elapsed(self):
        if self.recorder is None:
            self._tick = None
            return GLib.SOURCE_REMOVE
        seconds = int(time.monotonic() - self._started)
        self.status.set_text("Recording %s — %d:%02d" % (self._pending["title"], seconds // 60, seconds % 60))
        if seconds >= MAX_SECONDS:
            self.status.set_text("Reached the %d-minute limit; finishing…" % (MAX_SECONDS // 60))
            self.recorder.stop()
            self._tick = None
            return GLib.SOURCE_REMOVE
        return GLib.SOURCE_CONTINUE

    def _capture_done(self, ok, error):
        clip, self._pending, self.recorder = self._pending, None, None
        if self._tick is not None:
            GLib.source_remove(self._tick)
            self._tick = None
        path = self.store.path(clip)
        if ok and path.is_file() and path.stat().st_size > 0:
            self.store.add(clip)
            self.status.set_text("Saved %s." % clip["title"])
            self._refresh_gallery(select=len(self.store.clips) - 1)
            return
        path.unlink(missing_ok=True)
        if error:
            self.status.set_text("Nothing was saved: %s" % error)
        self._sync_controls()

    def _remove_clicked(self, _button):
        row = self.gallery.get_selected_row()
        if row is None:
            return
        title = self.store.clips[row.clip_index]["title"]
        self._show(None)
        self.store.remove(row.clip_index)
        self._refresh_gallery()
        self.status.set_text("Removed %s." % title)

    def _destroyed(self, _widget, directory):
        if self.recorder is not None:
            self.recorder.cancel()
        shutil.rmtree(directory, ignore_errors=True)

    # -- Journal -------------------------------------------------------

    def read_file(self, file_path):
        """Restore every capture from the Activity's Journal object."""
        self._show(None)
        if not self.store.load(file_path):
            self.status.set_text("This Journal entry has no recordings that can be opened.")
        elif self.store.clips:
            self.status.set_text("Restored %d recording%s." % (
                len(self.store.clips), "" if len(self.store.clips) == 1 else "s"))
        self._refresh_gallery(select=0 if self.store.clips else None)

    def write_file(self, file_path):
        """Save the manifest and finished captures; an unfinished one is dropped."""
        self.store.save(file_path)
