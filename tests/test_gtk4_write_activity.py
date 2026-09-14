from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_write_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-write-activity"
    info = (package / "activity/activity.info").read_text(); source = (package / "writeactivity4.py").read_text()
    assert "bundle_id = org.sugarlabs.Write" in info
    assert "sugar-activity4 writeactivity4.WriteActivity" in info
    assert "class WriteActivity(SimpleActivity)" in source
    assert "Document text" in source and "Save draft" in source
    assert "org.sugarlabs.Write" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-write-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-write-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
