from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_jumble_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-jumble-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "jumbleactivity4.py").read_text()
    assert "bundle_id = mulawa.Jumble" in info
    assert "class JumbleActivity(SimpleActivity)" in source
    assert "def _check" in source and "Next word" in source
    assert "def read_file" in source and "def write_file" in source
    assert "mulawa.Jumble" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
