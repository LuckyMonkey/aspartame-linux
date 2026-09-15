from pathlib import Path
ROOT = Path(__file__).parents[1]


def test_moon_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-moon-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "moonactivity4.py").read_text()
    assert "bundle_id = com.garycmartin.Moon" in info
    assert "sugar-activity4 moonactivity4.MoonActivity" in info
    assert "class MoonActivity(SimpleActivity)" in source
    assert "PHASES" in source and "set_draw_func" in source
    assert (package / "activity/moon.svg").is_file()
    matrix = (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "com.garycmartin.Moon|moonactivity4.MoonActivity" in matrix


def test_moon_journal_roundtrip_is_json():
    source = (ROOT / "packages/gtk4-moon-activity/moonactivity4.py").read_text()
    assert "def read_file(self, file_path)" in source
    assert "def write_file(self, file_path)" in source
    assert '"phase"' in source
