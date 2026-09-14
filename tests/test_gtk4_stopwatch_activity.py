from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_stopwatch_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-stopwatch-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "stopwatchactivity4.py").read_text()
    assert "bundle_id = org.sugarlabs.StopwatchActivity" in info
    assert "sugar-activity4 stopwatchactivity4.StopwatchActivity" in info
    assert "class StopwatchActivity(SimpleActivity)" in source
    assert "Elapsed time" in source
    assert "org.sugarlabs.StopwatchActivity" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-stopwatch-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-stopwatch-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
