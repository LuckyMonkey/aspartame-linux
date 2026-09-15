from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_colormyworld_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-colormyworld-activity"
    info = (package / "activity/activity.info").read_text(); source = (package / "colormyworldactivity4.py").read_text()
    assert "bundle_id = org.sugarlabs.ColorMyWorldActivity" in info
    assert "sugar-activity4 colormyworldactivity4.ColorMyWorldActivity" in info
    assert "class ColorMyWorldActivity(SimpleActivity)" in source
    assert "Selected color swatch" in source and "Red" in source
    assert "org.sugarlabs.ColorMyWorldActivity" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-colormyworld-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-colormyworld-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()


def test_colormyworld_journal_roundtrip_is_json():
    source = (ROOT / "packages/gtk4-colormyworld-activity/colormyworldactivity4.py").read_text()
    assert "def read_file(self, file_path)" in source
    assert "def write_file(self, file_path)" in source
    assert '"name"' in source
