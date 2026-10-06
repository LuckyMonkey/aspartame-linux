"""Small offline GTK4 Jukebox for the modern Sugar Space.

The original Jukebox can play arbitrary media. This port keeps the useful
playlist interaction self-contained for the shell: bundled demo tracks can be
selected and their play/stop state is visible without requiring a codec,
network, or media file in the test image. Local files use an optional native
GStreamer playbin when the guest provides an audio backend.
"""

import json
from pathlib import Path

import gi
try:
    gi.require_version("Gst", "1.0")
    from gi.repository import Gst
except (ImportError, ValueError):
    Gst = None

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


DEMO_TRACKS = (
    ("Morning Bell", "Demo track · 02:14"),
    ("Library Walk", "Demo track · 03:08"),
    ("Stars Above", "Demo track · 01:52"),
)


class JukeboxActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Jukebox")
        self._tracks = list(DEMO_TRACKS)
        self._selected = 0
        self._playing = False
        self._pipeline = None
        if Gst is not None:
            Gst.init(None)
        self._build()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        root.set_margin_top(28); root.set_margin_bottom(28)
        root.set_margin_start(32); root.set_margin_end(32)
        root.set_hexpand(True); root.set_vexpand(True)
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
        scroll = Gtk.ScrolledWindow(); scroll.set_child(self.playlist); scroll.set_hexpand(True); scroll.set_vexpand(True)
        playlist_frame = Gtk.Frame(label="Playlist"); playlist_frame.add_css_class("player-pane"); playlist_frame.set_hexpand(True); playlist_frame.set_vexpand(True); playlist_frame.set_child(scroll)

        player = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        player.set_margin_top(18); player.set_margin_bottom(18); player.set_margin_start(18); player.set_margin_end(18)
        player.set_hexpand(True); player.set_vexpand(True)
        player.set_valign(Gtk.Align.CENTER)
        self.now_playing = Gtk.Label(label="Nothing playing", xalign=0, wrap=True)
        self.now_playing.add_css_class("title-2")
        self.now_playing.update_property([Gtk.AccessibleProperty.LABEL], ["Now playing"])
        player.append(self.now_playing)
        player_hint = Gtk.Label(label="Choose a track from the playlist, then use the controls below.", xalign=0, wrap=True)
        player_hint.add_css_class("dim-label"); player.append(player_hint)
        player_frame = Gtk.Frame(label="Player"); player_frame.add_css_class("player-pane"); player_frame.set_hexpand(True); player_frame.set_vexpand(True); player_frame.set_child(player)

        panes = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        panes.set_hexpand(True); panes.set_vexpand(True)
        panes.set_wide_handle(True)
        panes.set_resize_start_child(True); panes.set_resize_end_child(True)
        panes.set_shrink_start_child(False); panes.set_shrink_end_child(False)
        panes.set_start_child(playlist_frame); panes.set_end_child(player_frame)
        # Give the playlist and player real space on first launch.  GTK4 does
        # not treat a negative position as an automatic split; it collapses
        # the leading child instead.
        panes.set_position(640)
        root.append(panes)
        self._refresh_playlist()

        self.status.set_hexpand(True)
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
        controls.set_halign(Gtk.Align.END)
        footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        footer.append(self.status)
        footer.append(controls)
        root.append(footer)
        self.set_canvas(root)
        self._install_css()

    def _install_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(b"frame.player-pane { border: 1px solid #8aa8b8; border-radius: 10px; padding: 8px; } listboxrow { padding: 12px; } listboxrow:selected { background: #dbeef7; } .track-title { font-weight: bold; } button { min-height: 40px; border-radius: 18px; }")
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _refresh_playlist(self):
        while (row := self.playlist.get_row_at_index(0)) is not None:
            self.playlist.remove(row)
        for index, track in enumerate(self._tracks):
            name, detail = track[:2]
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

    def _selected_track(self):
        track = self._tracks[self._selected]
        return track[0], track[1], track[2] if len(track) > 2 else None

    def _row_selected(self, _list, row):
        if row is None:
            return
        self._selected = row.track_index
        name, _detail, _uri = self._selected_track()
        if not self._playing and hasattr(self, "status"):
            self.status.set_text("Ready: %s" % name)
        self.now_playing.set_text("Ready: %s" % name)

    def _release_pipeline(self):
        if self._pipeline is None:
            return
        self._pipeline.get_bus().remove_signal_watch()
        self._pipeline.set_state(Gst.State.NULL)
        self._pipeline = None

    def _finish_playback(self, status):
        self._release_pipeline()
        self._playing = False
        self.status.set_text(status)
        self.now_playing.set_text(status)
        self.play.set_label("Play")
        self.play.set_sensitive(True)
        self.stop.set_sensitive(False)

    def _gst_message(self, _bus, message):
        if message.type == Gst.MessageType.EOS:
            self._finish_playback("Finished: %s" % self._selected_track()[0])
        elif message.type == Gst.MessageType.ERROR:
            error, _debug = message.parse_error()
            self._finish_playback("Playback error: %s" % error.message)

    def _play_selected(self, _button):
        row = self.playlist.get_selected_row()
        if row is not None:
            self._selected = row.track_index
        name, _detail, uri = self._selected_track()
        self._release_pipeline()
        if uri:
            if Gst is None:
                self.status.set_text("Audio backend unavailable: %s" % name)
                return
            self._pipeline = Gst.ElementFactory.make("playbin", "jukebox-playbin")
            if self._pipeline is None:
                self.status.set_text("Audio backend unavailable: %s" % name)
                return
            self._pipeline.set_property("uri", uri)
            bus = self._pipeline.get_bus()
            bus.add_signal_watch()
            bus.connect("message", self._gst_message)
            self._pipeline.set_state(Gst.State.PLAYING)
        self._playing = True
        self.status.set_text("Playing: %s" % name)
        self.now_playing.set_text("Playing: %s" % name)
        self.play.set_label("Playing")
        self.play.set_sensitive(False)
        self.stop.set_sensitive(True)

    def _stop(self, _button):
        self._finish_playback("Stopped: %s" % self._selected_track()[0])

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
            self._tracks.append((name, "Local file · ready to play", file_obj.get_uri()))
            self._selected = len(self._tracks) - 1
            self._refresh_playlist()
            self.status.set_text("Added: %s" % name)
            self.now_playing.set_text("Ready: %s" % name)

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
            if isinstance(track, list) and len(track) >= 2:
                values = (str(track[0]), str(track[1]))
                if len(track) > 2 and track[2]:
                    values += (str(track[2]),)
                restored.append(values)
        if restored:
            self._tracks = restored
        self._selected = max(0, min(int(payload.get("selected", 0)), len(self._tracks) - 1))
        self._playing = False
        self._refresh_playlist()
        self.status.set_text("Ready: %s" % self._selected_track()[0])
        self.now_playing.set_text("Ready: %s" % self._selected_track()[0])

    def write_file(self, file_path):
        """Save playlist and selected track as a JSON Journal object."""
        Path(file_path).write_text(json.dumps({"tracks": [list(track) for track in self._tracks], "selected": self._selected}, sort_keys=True) + "\n", encoding="utf-8")
