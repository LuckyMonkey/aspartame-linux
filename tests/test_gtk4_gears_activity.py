from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_gears_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-gears-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "gearsactivity4.py").read_text()
    assert "bundle_id = org.sugarlabs.GearsActivity" in info
    assert "sugar-activity4 gearsactivity4.GearsActivity" in info
    assert "class GearsActivity(SimpleActivity)" in source
    assert "set_draw_func" in source and "Turn gears" in source
    assert "def read_file" in source and "def write_file" in source
    assert "org.sugarlabs.GearsActivity" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-gears-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-gears-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
