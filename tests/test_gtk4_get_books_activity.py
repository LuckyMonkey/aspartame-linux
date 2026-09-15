from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_get_books_bundle_is_native_offline_and_registered():
    package = ROOT / "packages/gtk4-get-books-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "getbooksactivity4.py").read_text()
    assert "bundle_id = org.laptop.sugar.GetBooksActivity" in info
    assert "sugar-activity4 getbooksactivity4.GetBooksActivity" in info
    assert "class GetBooksActivity(SimpleActivity)" in source
    assert "Gtk.SearchEntry" in source and "Read selected book" in source
    assert "offline catalog" in source
    assert "org.laptop.sugar.GetBooksActivity|getbooksactivity4.GetBooksActivity" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    for script in ("sugar-gtk4-dev-sync.sh", "sugar-gtk4-build.sh"):
        assert "gtk4-get-books-activity" in (ROOT / "scripts" / script).read_text()


def test_get_books_journal_roundtrip_is_json():
    source = (ROOT / "packages/gtk4-get-books-activity/getbooksactivity4.py").read_text()
    assert "def read_file(self, file_path)" in source
    assert "def write_file(self, file_path)" in source
    assert '"selected"' in source
