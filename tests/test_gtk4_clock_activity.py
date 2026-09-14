from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_native_clock_bundle_is_staged_for_modern_space():
    info = (ROOT / "packages/gtk4-clock-activity/activity/activity.info").read_text()
    source = (ROOT / "packages/gtk4-clock-activity/clockactivity4.py").read_text()
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    run = (ROOT / "scripts/sugar-gtk4-run.sh").read_text()
    matrix = (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "bundle_id = org.aspartame.Clock" in info
    assert "sugar-activity4 clockactivity4.ClockActivity" in info
    assert "GLib.timeout_add_seconds(1, self._tick)" in source
    assert 'clock_activity="$repo/packages/gtk4-clock-activity"' in build
    assert "Clock.activity" in run
    assert "org.aspartame.Clock|clockactivity4.ClockActivity" in matrix
