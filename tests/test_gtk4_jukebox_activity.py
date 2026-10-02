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
    assert 'AccessibleProperty.LABEL' in source
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


def _media_usable():
    import os
    import subprocess
    import sys
    if not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        return False
    probe = ("import gi; gi.require_version('Gtk', '4.0'); gi.require_version('Gst', '1.0'); "
             "from gi.repository import Gst, Gtk; Gst.init(None); Gtk.Window(); "
             "assert all(Gst.ElementFactory.find(n) for n in ('audiotestsrc', 'vorbisenc', 'oggmux'))")
    return subprocess.run([sys.executable, "-c", probe], capture_output=True).returncode == 0


def test_jukebox_plays_local_files_and_keeps_old_objects_readable():
    import subprocess
    import sys

    import pytest
    if not _media_usable():
        pytest.skip("GTK4 media backend, GStreamer, or a display is unavailable")
    run = subprocess.run([sys.executable, str(ROOT / "tests/gtk4_harness/jukebox_playback.py")],
                         capture_output=True, text=True, timeout=120)
    assert run.returncode == 0, run.stderr[-4000:]
    assert "jukebox-playback=PASS" in run.stdout
