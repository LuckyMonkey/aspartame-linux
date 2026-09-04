from pathlib import Path


ROOT = Path(__file__).parents[1]
TOOLBAR = ROOT / 'sugar-overlay/src/jarabe/desktop/viewtoolbar.py'
HOME = ROOT / 'sugar-overlay/src/jarabe/desktop/homewindow.py'


def test_clock_is_centered_by_home_window_overlay_not_toolbar_flow():
    toolbar = TOOLBAR.read_text(encoding='utf-8')
    home = HOME.read_text(encoding='utf-8')
    assert 'def get_clock_widget' in toolbar
    assert 'self._clock_item = Gtk.ToolItem()' not in toolbar
    assert 'self._overlay = Gtk.Overlay()' in home
    assert 'self._overlay.add_overlay(self._clock)' in home
    assert "self._clock.set_halign(Gtk.Align.CENTER)" in home
    assert 'def __toolbar_size_allocate_cb' in home
