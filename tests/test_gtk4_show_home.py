from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_show_home_action_returns_to_home_zoom():
    patch = (ROOT / "patches/gtk4-preview/0100-shell-show-home-action.patch").read_text()
    assert "def ShowHome(self)" in patch
    assert "set_zoom_level(self._shell_model.ZOOM_HOME)" in patch


def test_show_home_patch_is_routed_and_idempotent():
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert '*0100*) target="$root/sources/sugar" ;;' in build
    assert "verified existing ShowHome action" in build
