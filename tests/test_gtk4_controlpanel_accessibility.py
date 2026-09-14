from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_controlpanel_section_tiles_are_keyboard_accessible():
    patch = (ROOT / "patches/gtk4-preview/0099-controlpanel-section-accessibility.patch").read_text()
    assert "set_accessible_role(Gtk.AccessibleRole.BUTTON)" in patch
    assert "Gdk.KEY_KP_Enter" in patch
    assert "Gdk.KEY_space" in patch


def test_controlpanel_accessibility_patch_is_routed():
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert '*0099*) target="$root/sources/sugar" ;;' in build
