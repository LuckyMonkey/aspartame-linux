from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_show_home_action_returns_to_home_zoom():
    patch = (ROOT / "patches/gtk4-preview/folded/0100-shell-show-home-action.patch").read_text()
    assert "def ShowHome(self)" in patch
    assert "set_zoom_level(self._shell_model.ZOOM_HOME)" in patch


