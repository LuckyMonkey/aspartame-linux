from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_iq_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-iq-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "iqactivity4.py").read_text()
    assert "bundle_id = mulawa.IQ" in info
    assert "sugar-activity4 iqactivity4.IQActivity" in info
    assert "class IQActivity(SimpleActivity)" in source
    assert "Next puzzle" in source
    assert "def read_file" in source and "def write_file" in source
    assert "mulawa.IQ" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-iq-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-iq-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
