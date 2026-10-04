from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_drawing_activities_do_not_shadow_simple_activity_canvas_property():
    """DrawingArea fields must not invoke SimpleActivity.canvas's setter."""
    for source_path in sorted((ROOT / "packages").glob("gtk4-*activity/*activity4.py")):
        source = source_path.read_text()
        if "Gtk.DrawingArea" in source:
            assert "self.canvas" not in source, source_path
