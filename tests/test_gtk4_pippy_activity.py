from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_pippy_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-pippy-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "pippyactivity4.py").read_text()
    assert "bundle_id = org.laptop.Pippy" in info
    assert "sugar-activity4 pippyactivity4.PippyActivity" in info
    assert "class PippyActivity(SimpleActivity)" in source
    assert 'label="Run"' in source and "Program output" in source
    assert 'OUTPUT_PLACEHOLDER = "Run the program to see output."' in source
    assert "subprocess.run" in source and '"-I"' in source
    assert "editor_frame" in source and "output_frame" in source
    assert "Gtk.Frame(label=\"Python program\")" in source
    assert "Gtk.Grid" in source and "set_column_homogeneous(True)" in source
    assert "frame.code-pane" in source
    matrix = (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "org.laptop.Pippy|pippyactivity4.PippyActivity" in matrix
    for script in ("sugar-gtk4-dev-sync.sh", "sugar-gtk4-build.sh"):
        assert "gtk4-pippy-activity" in (ROOT / "scripts" / script).read_text()


def test_pippy_journal_roundtrip_is_utf8():
    source = (ROOT / "packages/gtk4-pippy-activity/pippyactivity4.py").read_text()
    assert "def read_file(self, file_path)" in source
    assert "def write_file(self, file_path)" in source
    assert 'encoding="utf-8"' in source
