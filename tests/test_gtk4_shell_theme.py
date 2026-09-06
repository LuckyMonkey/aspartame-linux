import re
from pathlib import Path


ROOT = Path(__file__).parents[1]
PATCH_DIR = ROOT / "patches/gtk4-preview"


def test_gtk4_theme_is_staged_under_canonical_sugar_names():
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    runner = (ROOT / "scripts/sugar-gtk4-run.sh").read_text()
    css = (ROOT / "assets/gtk4/sugar.css").read_text()

    assert "for sugar_theme in sugar-72 sugar-100" in build
    assert '"$prefix/share/themes/$sugar_theme/gtk-4.0/gtk.css"' in build
    assert '"$prefix/share/themes/sugar-72/gtk-4.0/gtk.css"' in runner
    for selector in (".sugar-toolbar", ".toolbar", ".framewindow",
                     ".sugar-toolbarbox"):
        assert selector in css
    assert "#282828" in css


def test_gtk4_global_css_uses_a_display_provider():
    patch = (PATCH_DIR / "0026-toolkit-global-css.patch").read_text()
    assert "if widget is None:" in patch
    assert "Gtk.StyleContext.add_provider_for_display" in patch
    assert "Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION" in patch


def test_windowed_shell_frame_uses_viewport_geometry_and_native_chrome():
    patch = (PATCH_DIR / "0027-shell-windowed-frame.patch").read_text()
    assert "if not self._windowed:" in patch
    assert "self._container.set_size_request(-1, self.size)" in patch
    assert "self._event_area.show()" in patch
    assert "set_visible(delay != _MAX_DELAY)" in patch
    assert "set_decorated(False)" in patch


def test_every_numbered_preview_patch_is_explicitly_routed():
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    patch_ids = {path.name[:4] for path in PATCH_DIR.glob("*.patch")}
    routed_ids = set(re.findall(r"\*(\d{4})\*", build))
    assert routed_ids == patch_ids


def test_preview_build_rejects_unrouted_or_drifted_patches():
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert "unrouted GTK4 preview patch" in build
    assert 'patch_state="$root/build/applied-patches"' in build
    assert 'patch_digest=$(sha256sum "$patch"' in build
    assert 'grep -qx "$patch_digest" "$stamp"' in build
    assert "git -C \"$target\" apply --reverse --check" in build
    assert "GTK4 preview patch drift" in build
    assert "exit 2" in build
