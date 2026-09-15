from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_read_bundle_is_native_offline_and_registered():
    package = ROOT / "packages/gtk4-read-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "readactivity4.py").read_text()
    assert "bundle_id = org.laptop.sugar.ReadActivity" in info
    assert "sugar-activity4 readactivity4.ReadActivity" in info
    assert "class ReadActivity(SimpleActivity)" in source
    assert "DOCUMENT" in source and "Gtk.SearchEntry" in source
    assert "Previous page" in source and "Next page" in source
    assert "def read_file" in source
    assert "def write_file" in source
    assert 'encoding="utf-8"' in source
    assert 'text.split("\\f")' in source
    assert (package / "activity/read.svg").is_file()
    matrix = (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "org.laptop.sugar.ReadActivity|readactivity4.ReadActivity" in matrix
    for script in ("sugar-gtk4-dev-sync.sh", "sugar-gtk4-build.sh"):
        assert "gtk4-read-activity" in (ROOT / "scripts" / script).read_text()
