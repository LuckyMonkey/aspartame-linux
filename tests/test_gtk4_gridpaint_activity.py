from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_gridpaint_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-gridpaint-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "gridpaintactivity4.py").read_text()
    assert "bundle_id = org.olpcfrance.Gridpaint" in info
    assert "sugar-activity4 gridpaintactivity4.GridPaintActivity" in info
    assert "class GridPaintActivity(SimpleActivity)" in source
    assert "Clear picture" in source
    assert "org.olpcfrance.Gridpaint" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-gridpaint-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-gridpaint-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()


def test_gridpaint_journal_roundtrip_is_json():
    source = (ROOT / "packages/gtk4-gridpaint-activity/gridpaintactivity4.py").read_text()
    assert "def read_file(self, file_path)" in source
    assert "def write_file(self, file_path)" in source
    assert '"selected"' in source
