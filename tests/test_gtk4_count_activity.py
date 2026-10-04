from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "packages/gtk4-count-activity"


def test_count_is_a_native_gtk4_bundle():
    info = (PACKAGE / "activity/activity.info").read_text()
    source = (PACKAGE / "countactivity4.py").read_text()
    assert "exec = sugar-activity4 countactivity4.CountActivity" in info
    assert "from sugar4.activity import SimpleActivity" in source
    assert "Gtk.Grid" in source
    assert "Gtk.Button" in source
    assert "Gtk.GestureDrag" in source
    assert "_paint_rectangle" in source
    assert "AccessibleProperty.LABEL" in source
    assert "AccessibleRole.GROUP" in source
    assert "Gtk.Overlay" in source
    assert "Click or drag across cells to count objects" in source
    assert 'Gtk.Frame(label="Counting grid")' in source
    assert "Total objects across all layers" in source
    assert "require_version(\"Gtk\", \"3.0\")" not in source
    assert "if isinstance(layers, list):" in source
    assert "self.current_layer = max(0, self.current_layer)" in source
    assert "requested_layer = int(state.get(\"current_layer\", 0))" in source
    assert "len(layer) == self.height" in source
    assert "self._cells[0][0].grab_focus()" in source
    assert "grid.set_can_target(False)" in source
    assert "count-context-back" in source
    assert "count-context-front" in source
    assert "set_margin_start(relative * 18)" not in source


def test_gtk4_runner_stages_count_bundle():
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    run = (ROOT / "scripts/sugar-gtk4-run.sh").read_text()
    sync = (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-count-activity" in build
    assert "Count.activity" in run
    assert "gtk4-count-activity" in sync


def test_help_documents_count_layers_and_rectangle_painting():
    help_source = (ROOT / "packages/gtk4-help-activity/helpactivity4.py").read_text()
    assert '("Count Activity"' in help_source
    assert "translucent context" in help_source
    assert "drag across a rectangle" in help_source


def test_count_canvas_scales_from_its_allocated_surface():
    source = (PACKAGE / "countactivity4.py").read_text()
    assert "Gtk.AspectFrame.new" in source
    assert "self.width / self.height" in source
    assert "canvas_box.set_hexpand(True)" in source
    assert "self.grid.set_column_homogeneous(True)" in source
    assert "self.grid.set_row_homogeneous(True)" in source
    assert "x * self.width / grid_width" in source
    assert "x // 85" not in source
