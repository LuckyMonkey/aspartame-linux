from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_turtleart_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-turtleart-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "turtleartactivity4.py").read_text()
    assert "bundle_id = org.laptop.TurtleArtActivity" in info
    assert "sugar-activity4 turtleartactivity4.TurtleArtActivity" in info
    assert "class TurtleArtActivity(SimpleActivity)" in source
    assert "set_draw_func" in source and "Forward" in source
    assert "org.laptop.TurtleArtActivity" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-turtleart-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-turtleart-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
