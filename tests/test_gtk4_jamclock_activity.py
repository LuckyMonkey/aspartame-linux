from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_jamclock_modern_bundle_replaces_gtk3_entrypoint():
    info = (ROOT / "packages/gtk4-jamclock-activity/activity/activity.info").read_text()
    source = (ROOT / "packages/gtk4-jamclock-activity/jamclockactivity4.py").read_text()
    icon = ROOT / "packages/gtk4-jamclock-activity/activity/JAMClock.svg"
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    run = (ROOT / "scripts/sugar-gtk4-run.sh").read_text()
    matrix = (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "bundle_id = org.laptop.JAMClock" in info
    assert icon.is_file() and "#2f88bd" in icon.read_text()
    assert "sugar-activity4 jamclockactivity4.JAMClockActivity" in info
    assert "gi.require_version(\"Gtk\", \"4.0\")" in source
    assert 'jamclock_activity="$repo/packages/gtk4-jamclock-activity"' in build
    assert "JAMClock.activity" in run
    assert "org.laptop.JAMClock|jamclockactivity4.JAMClockActivity" in matrix
