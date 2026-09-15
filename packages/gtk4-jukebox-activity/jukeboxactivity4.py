"""Small offline GTK4 Jukebox for the modern Sugar Space.

The original Jukebox can play arbitrary media.  This port keeps the useful
playlist interaction self-contained for the shell: bundled demo tracks can be
selected and their play/stop state is visible without requiring a codec,
network, or media file in the test image.  Local files may also be added to
the playlist for a future media backend.
"""

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

        self.playlist = Gtk.ListBox(selection_mode=Gtk.SelectionMode.SINGLE)
        self.playlist.set_vexpand(True)
        self.playlist.update_property([Gtk.AccessibleProperty.LABEL], ["Playlist"])
        self.playlist.connect("row-selected", self._row_selected)
        scroll = Gtk.ScrolledWindow(); scroll.set_child(self.playlist); scroll.set_vexpand(True)
        root.append(scroll)
        self._refresh_playlist()

        self.status = Gtk.Label(label="Select a track to begin.", xalign=0)
        self.status.update_property([Gtk.AccessibleProperty.LABEL], ["Playback status"])
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
        for index, (name, detail) in enumerate(self._tracks):
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
        name = self._tracks[self._selected][0]
        self._playing = True
        self.status.set_text("Playing: %s" % name)
        self.play.set_label("Playing")
        self.play.set_sensitive(False)
        self.stop.set_sensitive(True)

    def _stop(self, _button):
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
            self._tracks.append((name, "Local file · playback backend pending"))
            self._selected = len(self._tracks) - 1
            self._refresh_playlist()
            self.status.set_text("Added: %s" % name)

