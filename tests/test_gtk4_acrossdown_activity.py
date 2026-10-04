from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_acrossdown_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-acrossdown-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "acrossdownactivity4.py").read_text()
    assert "bundle_id = mulawa.AcrossDown" in info
    assert "sugar-activity4 acrossdownactivity4.AcrossDownActivity" in info
    assert "class AcrossDownActivity(SimpleActivity)" in source
    assert "Check word" in source
    assert 'Gtk.Frame(label="Answer grid")' in source
    assert 'Gtk.Frame(label="Puzzle workspace")' in source
    assert "Gtk.CenterBox()" in source and "set_center_widget(workspace_frame)" in source
    assert "set_vexpand(True)" in source and "set_valign(Gtk.Align.CENTER)" in source
    assert "Solve one clue at a time" in source
    assert "Puzzle status" in source
    assert "def read_file" in source and "def write_file" in source
    assert "mulawa.AcrossDown" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-acrossdown-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-acrossdown-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
