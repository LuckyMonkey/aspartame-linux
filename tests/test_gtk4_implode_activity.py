from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_implode_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-implode-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "implodeactivity4.py").read_text()
    assert "bundle_id = com.jotaro.ImplodeActivity" in info
    assert "sugar-activity4 implodeactivity4.ImplodeActivity" in info
    assert "class ImplodeActivity(SimpleActivity)" in source
    assert "Reset puzzle" in source
    assert "com.jotaro.ImplodeActivity" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-implode-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-implode-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
