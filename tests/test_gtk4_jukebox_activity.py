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
