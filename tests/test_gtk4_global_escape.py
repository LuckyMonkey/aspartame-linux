from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_global_escape_only_consumes_a_revealed_frame():
    patch = (ROOT / "patches/gtk4-preview/0134-main-global-escape.patch").read_text()
    assert "Gtk.KeyvalTrigger.new(Gdk.KEY_Escape, 0)" in patch
    assert "if not frame_view.visible" in patch
    assert "frame_view.hide()" in patch
