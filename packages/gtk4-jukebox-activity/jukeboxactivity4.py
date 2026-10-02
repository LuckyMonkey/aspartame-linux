"""Small offline GTK4 Jukebox for the modern Sugar Space.

The original Jukebox can play arbitrary media.  This port keeps the useful
playlist interaction self-contained for the shell: bundled demo tracks can be
selected and their play/stop state is visible without requiring a codec,
network, or media file in the test image.  Local files added to the playlist
play through GTK4's own media backend (``Gtk.MediaFile``, GStreamer on Arch);
demo tracks have no audio and say so.

Journal objects store each track as ``[name, detail]`` or, since 2026-10-02,
``[name, detail, path]`` for a playable local file.  Both shapes are read.
"""

import json
from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


DEMO_TRACKS = (
    ("Morning Bell", "Demo track · 02:14"),
    ("Library Walk", "Demo track · 03:08"),
    ("Stars Above", "Demo track · 01:52"),
)
LOCAL_DETAIL = "Local file"


class JukeboxActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Jukebox")
        self._tracks = list(DEMO_TRACKS)
        self._selected = 0
        self._playing = False
        self._media = None
        self._build()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        root.set_margin_top(28); root.set_margin_bottom(28)
        root.set_margin_start(32); root.set_margin_end(32)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Jukebox audio player"])
        root.set_accessible_role(Gtk.AccessibleRole.GROUP)

        title = Gtk.Label(label="Jukebox", xalign=0)
        title.add_css_class("title-1")
        root.append(title)
        intro = Gtk.Label(
            label="Choose a track. Demo tracks show the player controls without requiring audio files.",
            xalign=0, wrap=True)
        intro.add_css_class("dim-label")
        root.append(intro)

        # Selecting the initial row reports through the status label, so it must
        # exist before the playlist is populated (it is appended below the list).
        self.status = Gtk.Label(label="Select a track to begin.", xalign=0)
        self.status.update_property([Gtk.AccessibleProperty.LABEL], ["Playback status"])
        self.playlist = Gtk.ListBox(selection_mode=Gtk.SelectionMode.SINGLE)
        self.playlist.set_vexpand(True)
        self.playlist.update_property([Gtk.AccessibleProperty.LABEL], ["Playlist"])
        self.playlist.connect("row-selected", self._row_selected)
        scroll = Gtk.ScrolledWindow(); scroll.set_child(self.playlist); scroll.set_vexpand(True)
        root.append(scroll)
        self._refresh_playlist()

        root.append(self.status)
        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.play = Gtk.Button(label="Play")
        self.play.update_property([Gtk.AccessibleProperty.LABEL], ["Play selected track"])
        self.play.connect("clicked", self._play_selected)
        self.stop = Gtk.Button(label="Stop")
        self.stop.update_property([Gtk.AccessibleProperty.LABEL], ["Stop playback"])
        self.stop.set_sensitive(False); self.stop.connect("clicked", self._stop)
        self.add = Gtk.Button(label="Add local track")
        self.add.update_property([Gtk.AccessibleProperty.LABEL], ["Add a local audio track"])
        self.add.connect("clicked", self._add_local)
        controls.append(self.play); controls.append(self.stop); controls.append(self.add)
        root.append(controls)
        self.set_canvas(root)
        self._install_css()

    def _install_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(b"listboxrow { padding: 12px; } .track-title { font-weight: bold; } button { min-height: 40px; border-radius: 18px; }")
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _refresh_playlist(self):
        while (row := self.playlist.get_row_at_index(0)) is not None:
            self.playlist.remove(row)
        for index, track in enumerate(self._tracks):
            name, detail = track[0], track[1]
            row = Gtk.ListBoxRow()
            row.track_index = index
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
            label = Gtk.Label(label=name, xalign=0); label.add_css_class("track-title")
            metadata = Gtk.Label(label=detail, xalign=0); metadata.add_css_class("dim-label")
            box.append(label); box.append(metadata); row.set_child(box)
            self.playlist.append(row)
        row = self.playlist.get_row_at_index(self._selected)
        if row is not None:
            self.playlist.select_row(row)

    def _row_selected(self, _list, row):
        if row is None:
            return
        self._selected = row.track_index
        if not self._playing:
            self.status.set_text("Ready: %s" % self._tracks[self._selected][0])

    def _play_selected(self, _button):
        row = self.playlist.get_selected_row()
        if row is not None:
            self._selected = row.track_index
        track = self._tracks[self._selected]
        name = track[0]
        path = track[2] if len(track) > 2 else None
        if path and not Path(path).is_file():
            self.status.set_text("Cannot play %s: the file is no longer there." % name)
            return
        self._release_media()
        if path:
            self._media = Gtk.MediaFile.new_for_filename(path)
            self._media.connect("notify::error", self._media_error)
            self._media.connect("notify::ended", self._media_ended)
            self._media.play()
            self.status.set_text("Playing: %s" % name)
        else:
            self.status.set_text("Playing: %s (demo track, no audio)" % name)
        self._playing = True
        self.play.set_label("Playing")
        self.play.set_sensitive(False)
        self.stop.set_sensitive(True)

    def _release_media(self):
        if self._media is not None:
            self._media.pause()
            self._media.clear()
            self._media = None

    def _media_error(self, media, _pspec):
        error = media.get_error()
        if error is not None:
            self._stop(None)
            self.status.set_text("Cannot play %s: %s" % (self._tracks[self._selected][0], error.message))

    def _media_ended(self, media, _pspec):
        if media.get_ended():
            self._stop(None)
            self.status.set_text("Finished: %s" % self._tracks[self._selected][0])

    def _stop(self, _button):
        self._release_media()
        self._playing = False
        self.status.set_text("Stopped: %s" % self._tracks[self._selected][0])
        self.play.set_label("Play")
        self.play.set_sensitive(True)
        self.stop.set_sensitive(False)

    def _add_local(self, _button):
        dialog = Gtk.FileDialog(title="Choose an audio file")
        dialog.open(self, None, self._file_chosen)

    def _file_chosen(self, dialog, result):
        try:
            file_obj = dialog.open_finish(result)
        except Exception:
            return
        if file_obj is not None:
            name = file_obj.get_basename() or "Local track"
            path = file_obj.get_path()
            if path:
                self._tracks.append((name, LOCAL_DETAIL, path))
            else:
                self._tracks.append((name, "Remote file · not playable offline"))
            self._selected = len(self._tracks) - 1
            self._refresh_playlist()
            self.status.set_text("Added: %s" % name)

    def read_file(self, file_path):
        """Restore playlist and selection from a JSON Journal object."""
        try:
            payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("payload must be an object")
            tracks = payload.get("tracks", [])
            if not isinstance(tracks, list):
                raise ValueError("tracks must be a list")
        except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
            return
        restored = []
        for track in tracks:
            if isinstance(track, list) and len(track) == 2:
                restored.append((str(track[0]), str(track[1])))
            elif isinstance(track, list) and len(track) == 3 and isinstance(track[2], str):
                restored.append((str(track[0]), str(track[1]), track[2]))
        if restored:
            self._tracks = restored
        try:
            selected = int(payload.get("selected", 0))
        except (TypeError, ValueError):
            selected = 0
        self._selected = max(0, min(selected, len(self._tracks) - 1))
        self._release_media()
        self._playing = False
        self._refresh_playlist()
        self.status.set_text("Ready: %s" % self._tracks[self._selected][0])

    def write_file(self, file_path):
        """Save playlist and selected track as a JSON Journal object."""
        Path(file_path).write_text(json.dumps({"tracks": self._tracks, "selected": self._selected}, sort_keys=True) + "\n", encoding="utf-8")
