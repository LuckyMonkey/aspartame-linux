from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_go_home_is_the_shared_gtk4_navigation_action():
    patch = (ROOT / "patches/gtk4-preview/0203-canonical-go-home-action.patch").read_text()
    assert "def go_home():" in patch
    assert "return actions.go_home()" in patch
    assert "actions.go_home()" in patch
    assert "if keyval == Gdk.KEY_F3:" in patch


def test_automation_surfaces_route_to_the_same_home_action():
    helper = (ROOT / "scripts/sugar-gtk4-action.py").read_text()
    macro = (ROOT / "macros/qemu/headless-go-home.json").read_text()
    assert 'choices=("home",)' in helper
    assert "shell.ShowHome()" in helper
    assert '"keys": "F3"' in macro


def test_go_home_patch_is_applied_to_the_gtk4_source_tree():
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    iso = (ROOT / "scripts/build-iso.sh").read_text()
    assert '*0203*) target="$root/sources/sugar" ;;' in build
    assert "sugar-gtk4-action.py" in iso
