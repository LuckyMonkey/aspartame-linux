from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_words_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-words-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "wordsactivity4.py").read_text()
    assert "bundle_id = org.laptop.Words" in info
    assert "sugar-activity4 wordsactivity4.WordsActivity" in info
    assert "class WordsActivity(SimpleActivity)" in source
    assert "Word to explore" in source
    assert "org.laptop.Words" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-words-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-words-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()


def test_words_journal_roundtrip_is_json():
    source = (ROOT / "packages/gtk4-words-activity/wordsactivity4.py").read_text()
    assert "def read_file(self, file_path)" in source
    assert "def write_file(self, file_path)" in source
    assert '"word"' in source
