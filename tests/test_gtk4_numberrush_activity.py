from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_numberrush_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-numberrush-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "numberrushactivity4.py").read_text()
    assert "bundle_id = org.sugarlabs.NumRush" in info
    assert "class NumberRushActivity(SimpleActivity)" in source
    assert "def _check" in source and "Next round" in source
    assert "org.sugarlabs.NumRush" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
