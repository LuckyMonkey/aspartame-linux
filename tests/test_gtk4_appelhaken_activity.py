from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_appelhaken_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-appelhaken-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "appelhakenactivity4.py").read_text()
    assert "bundle_id = mulawa.AppelHaken" in info
    assert "sugar-activity4 appelhakenactivity4.AppelHakenActivity" in info
    assert "class AppelHakenActivity(SimpleActivity)" in source
    assert "Reset puzzle" in source
    assert "def read_file" in source and "def write_file" in source
    assert "mulawa.AppelHaken" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-appelhaken-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-appelhaken-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
