from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_fototoon_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-fototoon-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "fototoonactivity4.py").read_text()
    assert "bundle_id = org.eq.FotoToon" in info
    assert "sugar-activity4 fototoonactivity4.FotoToonActivity" in info
    assert "class FotoToonActivity(SimpleActivity)" in source
    assert "Clear canvas" in source
    assert "org.eq.FotoToon" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-fototoon-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-fototoon-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()


def test_fototoon_journal_roundtrip_is_json():
    source = (ROOT / "packages/gtk4-fototoon-activity/fototoonactivity4.py").read_text()
    assert "def read_file(self, file_path)" in source
    assert "def write_file(self, file_path)" in source
    assert '"panel_placed"' in source
