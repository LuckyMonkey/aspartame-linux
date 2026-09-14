from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_show_list_action_targets_native_home_list():
    patch = (ROOT / "patches/gtk4-preview/0101-shell-show-list-action.patch").read_text()
    assert "def show_list_view(self)" in patch
    assert "def ShowList(self)" in patch
    assert "get_home_box().show_list_view()" in patch


def test_show_list_patch_is_routed_and_idempotent():
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert '*0101*) target="$root/sources/sugar" ;;' in build
    assert "verified existing ShowList action" in build
