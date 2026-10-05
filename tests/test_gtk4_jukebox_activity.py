from pathlib import Path


ROOT = Path(__file__).parents[1]
PACKAGE = ROOT / "packages/gtk4-jukebox-activity"


def test_jukebox_is_native_offline_and_accessible():
    info = (PACKAGE / "activity/activity.info").read_text()
    source = (PACKAGE / "jukeboxactivity4.py").read_text()
    assert "org.laptop.sugar.Jukebox" in info
    assert "sugar-activity4 jukeboxactivity4.JukeboxActivity" in info
    assert "DEMO_TRACKS" in source
    assert "Gtk.ListBox" in source and "Gtk.FileDialog" in source
    assert "playlist_frame" in source and "Gtk.Frame(label=\"Playlist\")" in source
    assert "Gtk.Paned" in source and "set_start_child(playlist_frame)" in source
    assert "set_end_child(player_frame)" in source
    assert "root.append(panes)" in source
    assert 'Gtk.Frame(label="Player")' in source
    assert "now_playing" in source
    assert "footer.append(self.status)" in source
    assert "listboxrow:selected" in source
    assert 'AccessibleProperty.LABEL' in source
    assert 'Gst.ElementFactory.make("playbin"' in source
    assert 'file_obj.get_uri()' in source
    assert "Local file · ready to play" in source
    assert "require_version(\"Gtk\", \"3.0\")" not in source


def test_jukebox_is_staged_and_registered():
    for script in ("sugar-gtk4-build.sh", "sugar-gtk4-dev-sync.sh"):
        assert "gtk4-jukebox-activity" in (ROOT / "scripts" / script).read_text()
    matrix = (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "org.laptop.sugar.Jukebox|jukeboxactivity4.JukeboxActivity" in matrix


def test_jukebox_journal_roundtrip_is_json():
    source = (PACKAGE / "jukeboxactivity4.py").read_text()
    assert "def read_file(self, file_path)" in source
    assert "def write_file(self, file_path)" in source
    assert '"tracks"' in source


def test_jukebox_roundtrip_can_capture_the_resumed_player_surface():
    probe = (ROOT / "scripts/sugar-gtk4-jukebox-roundtrip.py").read_text()
    assert '"ffmpeg"' in probe
    assert '"Field Recording"' in probe
    assert "x11grab" in probe
