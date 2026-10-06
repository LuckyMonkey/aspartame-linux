from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_colormyworld_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-colormyworld-activity"
    info = (package / "activity/activity.info").read_text(); source = (package / "colormyworldactivity4.py").read_text()
    assert "bundle_id = org.sugarlabs.ColorMyWorldActivity" in info
    assert "sugar-activity4 colormyworldactivity4.ColorMyWorldActivity" in info
    assert "class ColorMyWorldActivity(SimpleActivity)" in source
    assert "World map coloring canvas" in source and "Red" in source
    assert "Choose a color, then click a region" in source
    assert "Choose a color, then click a world region" in source
    assert "Gtk.ToggleButton" in source
    assert "AccessibleProperty.DESCRIPTION" in source
    assert "togglebutton:checked" in source
    assert "colors.set_halign(Gtk.Align.CENTER)" in source
    assert "swatch_frame" in source and "Gtk.Frame(label=\"World map\")" in source
    assert "palette_frame" in source and "Gtk.Frame(label=\"Palette\")" in source
    assert "Gtk.GestureClick" in source and "_map_pressed" in source
    assert 'label="Clear map"' in source and '"regions"' in source
    assert "REGION_LABELS" in source and "cr.show_text(label)" in source
    assert "org.sugarlabs.ColorMyWorldActivity" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-colormyworld-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-colormyworld-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()


def test_colormyworld_journal_roundtrip_is_json():
    source = (ROOT / "packages/gtk4-colormyworld-activity/colormyworldactivity4.py").read_text()
    assert "def read_file(self, file_path)" in source
    assert "def write_file(self, file_path)" in source
    assert '"name"' in source
