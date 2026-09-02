from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_gtk4_build_stages_shell_runtime_data_before_launch():
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    launcher = (ROOT / "scripts/sugar-gtk4-run.sh").read_text()
    assert 'SUGAR_MIME_DEFAULTS="$shell/data/mime.defaults"' in launcher
    assert 'cp -a "$shell/extensions/." "$prefix/share/sugar/extensions/"' in build
    assert 'test -d "$prefix/share/sugar/extensions"' in launcher
    assert 'ln -sfn "$shell/extensions"' not in launcher


def test_gtk4_launcher_seeds_private_bus_environment_first():
    launcher = (ROOT / "scripts/sugar-gtk4-run.sh").read_text()
    assert 'locale_name=${LANG:-C.UTF-8}' in launcher
    assert 'LANG="$locale_name"' in launcher
    assert 'XDG_RUNTIME_DIR="$runroot"' in launcher
    assert launcher.index("exec env") < launcher.index("dbus-run-session --")


def test_gtk4_session_fails_when_datastore_never_registers():
    session = (ROOT / "scripts/sugar-gtk4-session.sh").read_text()
    assert 'datastore_ready=0' in session
    assert 'if [ "$datastore_ready" -ne 1 ]' in session


def test_gtk4_home_preview_patches_are_ordered_and_targeted():
    patches = sorted((ROOT / "patches/gtk4-preview").glob("00*.patch"))
    names = [patch.name for patch in patches]
    assert names[-17:] == [
        "0005-home-cell-renderer-api.patch",
        "0006-profile-modern-ssh-key.patch",
        "0007-home-renderer-signal-compat.patch",
        "0008-home-lazy-legacy-list.patch",
        "0009-home-lazy-list-signal.patch",
        "0010-home-defer-optional-views.patch",
        "0011-frame-neighborhood-optional.patch",
        "0012-home-lazy-list-search.patch",
        "0013-toolkit-palette-icon-compat.patch",
        "0014-datastore-use-sugar4-modules.patch",
        "0015-toolkit-cell-renderer-props-compat.patch",
        "0016-toolkit-cell-renderer-gobject.patch",
        "0017-toolkit-icon-file-alias.patch",
        "0018-toolkit-datastore-dbus-contract.patch",
        "0019-home-icon-pixel-size.patch",
        "0020-toolkit-cell-renderer-scrolling.patch",
        "0021-home-retain-toolbar.patch",
    ]
    text = "\n".join(p.read_text() for p in patches[-17:])
    assert "CellRendererFavorite" in text
    assert "supported_prefixes" in text
    assert "_ensure_group_box" in text
    assert "Neighborhood unavailable for FriendsTray" in text
    assert "child.set_pixel_size(icon_size)" in text
    assert "def connect_to_scroller(self, scrolled):" in text
    assert "self._toolbar = toolbar" in text
