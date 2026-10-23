"""Native GTK4 Jukebox Activity.

A port of GTK3 Jukebox (sugarlabs/jukebox-activity): play audio and video
from the Journal or local files, keep them in a playlist (previous/next,
reorder, remove), seek, and watch video full screen. Playback uses
Gtk.MediaFile, GTK's GStreamer-backed media stream.

The Journal payload is the GTK3 M3U playlist. Opened from a song or video,
Jukebox plays it, leaves that object's bytes alone, and saves any playlist
built from it as a separate Journal object, as GTK3 does.
"""

import json
from pathlib import Path

from gi.repository import Gdk, Gio, GLib, Gtk, Pango
from sugar4.activity import SimpleActivity

from jukebox_playlist import (M3U_MIME, Playlist, from_legacy_json, is_media, is_playlist,
                              journal_id, journal_path, parse_m3u, write_m3u)


class Journal:
    """The Journal, through the sugar4 datastore."""

    def media(self, limit=200):
        from sugar4.datastore import datastore
        entries, _count = datastore.find({}, sorting=["-timestamp"], limit=limit,
                                         properties=["uid", "title", "mime_type"])
        found = []
        for entry in entries:
            meta = entry.get_metadata()
            if is_media(meta.get("mime_type")):
                found.append((entry.object_id, str(meta.get("title") or "Untitled"),
                              str(meta.get("mime_type"))))
            entry.destroy()
        return found

    def open(self, object_id):
        """A DSObject whose file stays on disk until destroyed."""
        from sugar4.datastore import datastore
        entry = datastore.get(object_id)
        if entry is None or not entry.get_file_path():
            raise FileNotFoundError("Journal entry %s is gone" % object_id)
        return entry

    def save_playlist(self, entry, title, text, bundle_id):
        from sugar4.datastore import datastore
        if entry is None:
            entry = datastore.create()
            entry.metadata["mime_type"] = M3U_MIME
            entry.metadata["activity"] = bundle_id
        entry.metadata["title"] = title
        entry.metadata["description"] = text
        path = Path(GLib.get_tmp_dir()) / ("jukebox-%d.m3u" % id(entry))
        path.write_text(text, encoding="utf-8")
        entry.file_path = str(path)
        datastore.write(entry, transfer_ownership=True)
        return entry


def clock(microseconds):
    seconds = max(0, int(microseconds // 1_000_000))
    return "%d:%02d" % divmod(seconds, 60)


class JukeboxActivity(SimpleActivity):
    BUNDLE_ID = "org.laptop.sugar.Jukebox"

    def __init__(self, activity_handle=None, journal=None):
        super().__init__(activity_handle)
        self.set_title("Jukebox")
        self.journal = journal or Journal()
        self.playlist = Playlist()
        self.media = None
        self._entry = None            # DSObject backing the current track
        self._source_media = None     # (object id, title) when opened from media
        self._playlist_entry = None   # separate playlist object for that case
        self._tick = 0
        self._seeking = False
        self._build()
        self._refresh()

    # Layout

    def _button(self, label, tip, handler, *args, name=None):
        button = Gtk.Button(label=label)
        button.set_tooltip_text(tip)
        if name:
            button.update_property([Gtk.AccessibleProperty.LABEL], [name])
        button.connect("clicked", handler, *args)
        return button

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        root.set_margin_top(18); root.set_margin_bottom(18)
        root.set_margin_start(24); root.set_margin_end(24)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Jukebox"])

        header = Gtk.Box(spacing=8)
        title = Gtk.Label(label="Jukebox", xalign=0, hexpand=True)
        title.add_css_class("title-1")
        header.append(title)
        self.playlist_toggle = Gtk.ToggleButton(label="Playlist", active=True)
        self.playlist_toggle.set_tooltip_text("Show or hide the playlist")
        self.playlist_toggle.connect("toggled", self._toggle_playlist)
        header.append(self.playlist_toggle)
        header.append(self._button("Fullscreen", "Fill the screen with the video (Escape leaves)",
                                   self._fullscreen))
        root.append(header)

        self.side = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.side.set_size_request(340, -1)
        self.tracks = Gtk.ListBox()
        self.tracks.update_property([Gtk.AccessibleProperty.LABEL], ["Playlist"])
        self.tracks.connect("row-activated", lambda _l, row: self._play_index(row.get_index()))
        empty = Gtk.Label(label="The playlist is empty. Add songs or videos from the Journal.",
                          wrap=True)
        empty.add_css_class("dim-label")
        self.tracks.set_placeholder(empty)
        scroll = Gtk.ScrolledWindow(vexpand=True)
        scroll.set_child(self.tracks)
        frame = Gtk.Frame(label="Playlist")
        frame.set_child(scroll)
        self.side.append(frame)
        edit = Gtk.FlowBox(selection_mode=Gtk.SelectionMode.NONE, max_children_per_line=3)
        for widget in (
                self._button("Add from Journal", "Choose songs and videos from the Journal",
                             self._show_picker),
                self._button("Add file", "Add a song or video file", self._add_file),
                self._button("Remove track", "Remove the selected track", self._remove),
                self._button("Move up", "Move the selected track earlier", self._move, -1),
                self._button("Move down", "Move the selected track later", self._move, 1)):
            edit.append(widget)
        self.side.append(edit)

        self.picker = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        picker_header = Gtk.Box(spacing=8)
        picker_title = Gtk.Label(label="Journal songs and videos", xalign=0, hexpand=True)
        picker_title.add_css_class("heading")
        picker_header.append(picker_title)
        picker_header.append(self._button("Done", "Close the Journal list", self._hide_picker,
                                          name="Close Journal list"))
        self.picker.append(picker_header)
        self.picker_list = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE)
        self.picker_list.update_property([Gtk.AccessibleProperty.LABEL], ["Journal media"])
        picker_scroll = Gtk.ScrolledWindow(vexpand=True)
        picker_scroll.set_child(self.picker_list)
        self.picker.append(picker_scroll)
        self.picker.set_visible(False)
        self.side.append(self.picker)

        stage = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, hexpand=True)
        self.screen = Gtk.Overlay(vexpand=True)
        self.video = Gtk.Picture(can_shrink=True, content_fit=Gtk.ContentFit.CONTAIN)
        self.video.add_css_class("video")
        self.video.update_property([Gtk.AccessibleProperty.LABEL], ["Video"])
        self.screen.set_child(self.video)
        self.now_playing = Gtk.Label(label="Nothing playing", wrap=True, justify=Gtk.Justification.CENTER)
        self.now_playing.add_css_class("title-2")
        self.now_playing.set_halign(Gtk.Align.CENTER); self.now_playing.set_valign(Gtk.Align.CENTER)
        self.now_playing.update_property([Gtk.AccessibleProperty.LABEL], ["Now playing"])
        self.screen.add_overlay(self.now_playing)
        stage.append(self.screen)

        seek = Gtk.Box(spacing=8)
        self.position = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 1, 1)
        self.position.set_draw_value(False)
        self.position.set_hexpand(True)
        self.position.update_property([Gtk.AccessibleProperty.LABEL], ["Playback position"])
        self.position.connect("value-changed", self._seek)
        seek.append(self.position)
        self.time = Gtk.Label(label="0:00 / 0:00")
        self.time.update_property([Gtk.AccessibleProperty.LABEL], ["Playback time"])
        seek.append(self.time)
        stage.append(seek)

        controls = Gtk.Box(spacing=8, halign=Gtk.Align.CENTER)
        self.prev_button = self._button("Previous", "Play the previous track", self._step, -1)
        self.play_button = self._button("Play", "Play or pause", self._play_pause)
        self.next_button = self._button("Next", "Play the next track", self._step, 1)
        for button in (self.prev_button, self.play_button, self.next_button):
            controls.append(button)
        stage.append(controls)

        panes = Gtk.Paned(vexpand=True, shrink_start_child=False, resize_start_child=False)
        panes.set_start_child(self.side)
        panes.set_end_child(stage)
        # GTK4 collapses a Paned without an explicit position.
        panes.set_position(380)
        root.append(panes)

        self.status = Gtk.Label(label="Add songs or videos to begin.", xalign=0, wrap=True)
        self.status.add_css_class("dim-label")
        self.status.update_property([Gtk.AccessibleProperty.LABEL], ["Playback status"])
        root.append(self.status)
        self.set_canvas(root)

        keys = Gtk.EventControllerKey()
        keys.connect("key-pressed", self._key)
        self.add_controller(keys)
        provider = Gtk.CssProvider()
        provider.load_from_data(
            b"button { min-height: 40px; border-radius: 18px; } listboxrow { padding: 8px; }"
            b" picture.video { background: #101418; border-radius: 8px; }"
            b" .current { font-weight: bold; }")
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    # Playlist view

    def _refresh(self, message=None):
        self.tracks.remove_all()
        for index, track in enumerate(self.playlist.tracks):
            source = "Journal" if journal_id(track["path"]) else "File"
            label = Gtk.Label(label="%d. %s" % (index + 1, track["title"]), xalign=0,
                              ellipsize=Pango.EllipsizeMode.END)
            label.set_tooltip_text("%s · %s" % (track["title"], source))
            if index == self.playlist.current:
                label.add_css_class("current")
            self.tracks.append(label)
            row = self.tracks.get_row_at_index(index)
            row.update_property([Gtk.AccessibleProperty.LABEL],
                                ["%s, track %d, from %s" % (track["title"], index + 1, source)])
        if 0 <= self.playlist.current < len(self.playlist):
            self.tracks.select_row(self.tracks.get_row_at_index(self.playlist.current))
        has = len(self.playlist) > 0
        self.play_button.set_sensitive(has)
        self.prev_button.set_sensitive(self.playlist.current > 0)
        self.next_button.set_sensitive(0 <= self.playlist.current < len(self.playlist) - 1)
        if message:
            self.status.set_text(message)

    def _selected(self):
        row = self.tracks.get_selected_row()
        return row.get_index() if row is not None else self.playlist.current

    def _remove(self, _button):
        index = self._selected()
        if not 0 <= index < len(self.playlist):
            return
        title = self.playlist.tracks[index]["title"]
        if index == self.playlist.current:
            self._stop_media()
        self.playlist.remove(index)
        self._refresh("Removed %s" % title)

    def _move(self, _button, step):
        index = self._selected()
        moved = self.playlist.move(index, step)
        self._refresh()
        if moved != index:
            self.tracks.select_row(self.tracks.get_row_at_index(moved))
            self.status.set_text("Moved %s to position %d" % (self.playlist.tracks[moved]["title"], moved + 1))

    def _toggle_playlist(self, button):
        self.side.set_visible(button.get_active())

    def _fullscreen(self, _button):
        self.playlist_toggle.set_active(False)
        self.fullscreen()

    def _key(self, _controller, keyval, _keycode, _state):
        if keyval == Gdk.KEY_Escape and self.is_fullscreen():
            self.unfullscreen()
            self.playlist_toggle.set_active(True)
            return True
        return False

    # Journal picker

    def _show_picker(self, _button):
        self.picker_list.remove_all()
        try:
            media = self.journal.media()
        except Exception as error:
            self.status.set_text("Cannot read the Journal: %s" % error)
            return
        for object_id, title, mime_type in media:
            kind = "video" if mime_type.startswith("video/") else "audio"
            button = self._button("%s (%s)" % (title, kind), "Add to the playlist",
                                  self._pick, object_id, title,
                                  name="Add %s to playlist" % title)
            self.picker_list.append(button)
        if not media:
            self.picker_list.append(Gtk.Label(label="No songs or videos in the Journal yet."))
        self.picker.set_visible(True)
        self.status.set_text("%d songs and videos in the Journal" % len(media))
        first = self.picker_list.get_row_at_index(0)
        if first is not None and isinstance(first.get_child(), Gtk.Button):
            first.get_child().grab_focus()

    def _hide_picker(self, _button):
        self.picker.set_visible(False)

    def _pick(self, _button, object_id, title):
        index = self.playlist.add(title, journal_path(object_id))
        self._refresh("Added %s" % title)
        if self.media is None or not self.media.get_playing():
            self.playlist.current = index
            self._refresh()

    def _add_file(self, _button):
        dialog = Gtk.FileDialog(title="Choose a song or video")
        dialog.open(self, None, self._file_chosen)

    def _file_chosen(self, dialog, result):
        try:
            chosen = dialog.open_finish(result)
        except GLib.Error:
            return
        if chosen is not None:
            self.playlist.add(chosen.get_basename() or "Track", chosen.get_uri())
            self._refresh("Added %s" % chosen.get_basename())

    # Playback

    def _stop_media(self):
        if self.media is not None:
            self.media.set_playing(False)
            self.media.disconnect_by_func(self._media_changed)
            self.video.set_paintable(None)
            self.media = None
        if self._tick:
            GLib.source_remove(self._tick)
            self._tick = 0
        if self._entry is not None:
            self._entry.destroy()
            self._entry = None

    def _open_track(self, track):
        object_id = journal_id(track["path"])
        if object_id:
            self._entry = self.journal.open(object_id)
            return Gio.File.new_for_path(self._entry.get_file_path())
        if track["path"].startswith("/"):
            return Gio.File.new_for_path(track["path"])
        return Gio.File.new_for_uri(track["path"])

    def _play_index(self, index):
        self._stop_media()
        self.playlist.current = index
        track = self.playlist.track
        if track is None:
            return
        try:
            media_file = self._open_track(track)
        except (OSError, GLib.Error) as error:
            self._refresh("Cannot open %s: %s" % (track["title"], error))
            return
        self.media = Gtk.MediaFile.new_for_file(media_file)
        self.media.connect("notify", self._media_changed)
        self.video.set_paintable(self.media)
        self.media.play()
        self._tick = GLib.timeout_add(500, self._update_position)
        self.now_playing.set_text(track["title"])
        self.now_playing.set_visible(True)
        self._refresh("Playing: %s" % track["title"])
        self.play_button.set_label("Pause")

    def _media_changed(self, media, pspec):
        name = pspec.get_name()
        track = self.playlist.track
        title = track["title"] if track else ""
        if name == "error" and media.get_error() is not None:
            self.status.set_text("Cannot play %s: %s" % (title, media.get_error().message))
            self.play_button.set_label("Play")
        elif name == "prepared" and media.is_prepared():
            self.now_playing.set_visible(not media.has_video())
            duration = media.get_duration()
            self.position.set_range(0, max(1, duration))
        elif name == "playing":
            self.play_button.set_label("Pause" if media.get_playing() else "Play")
            if not media.get_ended():
                self.status.set_text(("Playing: %s" if media.get_playing() else "Paused: %s") % title)
        elif name == "ended" and media.get_ended():
            if self.playlist.step(1):
                self._play_index(self.playlist.current)
            else:
                self.status.set_text("Finished: %s" % title)
                self.play_button.set_label("Play")
                self.now_playing.set_visible(True)

    def _update_position(self):
        if self.media is None:
            self._tick = 0
            return False
        now, total = self.media.get_timestamp(), self.media.get_duration()
        self._seeking = True
        self.position.set_value(now)
        self._seeking = False
        self.time.set_text("%s / %s" % (clock(now), clock(total)))
        self.position.update_property([Gtk.AccessibleProperty.VALUE_TEXT],
                                      ["%s of %s" % (clock(now), clock(total))])
        return True

    def _seek(self, scale):
        if not self._seeking and self.media is not None and self.media.is_seekable():
            self.media.seek(int(scale.get_value()))

    def _play_pause(self, _button):
        if self.media is None or self.media.get_ended():
            index = self._selected()
            self._play_index(index if 0 <= index < len(self.playlist) else 0)
        elif self.media.get_playing():
            self.media.pause()
        else:
            self.media.play()

    def _step(self, _button, direction):
        if self.playlist.step(direction):
            self._play_index(self.playlist.current)

    # Journal

    def _object_id(self):
        jobject = getattr(self, "_jobject", None)
        return getattr(jobject, "object_id", None)

    def read_file(self, file_path):
        """Open a playlist, or a song/video to play; anything else raises."""
        meta = self.metadata or {}
        mime_type = meta.get("mime_type", "")
        if is_media(mime_type) and not is_playlist(mime_type):
            object_id = self._object_id()
            title = str(meta.get("title") or "Track")
            self._source_media = (object_id, title)
            self.playlist = Playlist()
            self.playlist.add(title, journal_path(object_id) if object_id else str(file_path))
            self._refresh()
            GLib.idle_add(lambda: self._play_index(0) and False)
            return
        text = Path(file_path).read_text(encoding="utf-8")
        if text.lstrip().startswith("{"):
            tracks = from_legacy_json(json.loads(text))
        else:
            tracks = parse_m3u(text)
        self.playlist = Playlist(tracks)
        self._refresh("Playlist of %d tracks" % len(tracks))

    def write_file(self, file_path):
        """Save the playlist as M3U, never over a song or video."""
        text = write_m3u(self.playlist.tracks)
        if self._source_media is not None:
            object_id, title = self._source_media
            single = [{"title": title, "path": journal_path(object_id)}]
            if self.playlist.tracks != single:
                self._playlist_entry = self.journal.save_playlist(
                    self._playlist_entry, "%s playlist" % title, text, self.BUNDLE_ID)
            # Leaves the media object's file untouched; metadata still saves.
            raise NotImplementedError("Jukebox keeps the media object unchanged")
        if self.metadata is not None:
            self.metadata["mime_type"] = M3U_MIME
            self.metadata["description"] = "\n".join(t["title"] for t in self.playlist.tracks)
        Path(file_path).write_text(text, encoding="utf-8")

    def can_close(self):
        self._stop_media()
        return super().can_close()
