from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "packages/gtk4-level-activity"


def test_level_is_native_gtk4_and_interactive():
    info = (PACKAGE / "activity/activity.info").read_text()
    source = (PACKAGE / "levelactivity4.py").read_text()
    assert "net.flossmanuals.LevelActivity" in info
    assert "sugar-activity4 levelactivity4.LevelActivity" in info
    assert "Gtk.DrawingArea" in source
    assert "Gtk.GestureDrag" in source
    assert '"Reset"' in source
    assert "AccessibleProperty.LABEL" in source
    assert 'require_version("Gtk", "3.0")' not in source


def test_level_is_staged_and_matrix_registered():
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    sync = (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    matrix = (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-level-activity" in build
    assert "gtk4-level-activity" in sync
    assert "net.flossmanuals.LevelActivity|levelactivity4.LevelActivity" in matrix
