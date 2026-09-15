from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_activity_focus_ring_is_gtk4_native_and_visible():
    patch = (ROOT / "patches/gtk4-preview/0135-toolkit-visible-focus-ring.patch").read_text()
    assert "button:focus" in patch
    assert "outline-style: solid" in patch
    assert "Gtk.StyleContext.add_provider_for_display" in patch
