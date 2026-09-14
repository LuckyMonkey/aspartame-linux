from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_journal_rows_expose_native_copy_drag_source():
    source = (ROOT / "gtk4-overlay/src/jarabe/journal/listview.py").read_text()
    assert "Gtk.DragSource()" in source
    assert "Gdk.DragAction.COPY" in source
    assert "Gdk.ContentProvider.new_for_bytes('text/plain'" in source
    assert "def is_dragging(self): return self._dragging" in source
