from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_paint_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-paint-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "paintactivity4.py").read_text()
    assert "bundle_id = org.sugarlabs.Paint" in info
    assert "sugar-activity4 paintactivity4.PaintActivity" in info
    assert "class PaintActivity(SimpleActivity)" in source
    assert "Gtk.GestureDrag" in source and "set_draw_func" in source
    assert (package / "activity/paint.svg").is_file()
    assert "org.sugarlabs.Paint|paintactivity4.PaintActivity" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    for path in ("scripts/sugar-gtk4-dev-sync.sh", "scripts/sugar-gtk4-build.sh"):
        assert "gtk4-paint-activity" in (ROOT / path).read_text()


def test_paint_journal_roundtrip_is_json():
    source = (ROOT / "packages/gtk4-paint-activity/paintactivity4.py").read_text()
    assert "def read_file(self, file_path)" in source
    assert "def write_file(self, file_path)" in source
    assert '"strokes"' in source
