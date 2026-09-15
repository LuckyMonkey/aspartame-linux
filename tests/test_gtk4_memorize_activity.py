from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_memorize_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-memorize-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "memorizeactivity4.py").read_text()
    assert "bundle_id = org.laptop.Memorize" in info
    assert "sugar-activity4 memorizeactivity4.MemorizeActivity" in info
    assert "class MemorizeActivity(SimpleActivity)" in source
    assert "New game" in source
    assert "def read_file" in source and "def write_file" in source
    assert "org.laptop.Memorize" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-memorize-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-memorize-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
