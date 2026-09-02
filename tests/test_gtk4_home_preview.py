from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_gtk4_launcher_stages_shell_runtime_data():
    launcher = (ROOT / "scripts/sugar-gtk4-run.sh").read_text()
    assert 'SUGAR_MIME_DEFAULTS="$shell/data/mime.defaults"' in launcher
    assert 'ln -sfn "$shell/extensions" "$prefix/share/sugar/extensions"' in launcher


def test_gtk4_home_preview_patches_are_ordered_and_targeted():
    patches = sorted((ROOT / "patches/gtk4-preview").glob("00*.patch"))
    names = [patch.name for patch in patches]
    assert names[-7:] == [
        "0005-home-cell-renderer-api.patch",
        "0006-profile-modern-ssh-key.patch",
        "0007-home-renderer-signal-compat.patch",
        "0008-home-lazy-legacy-list.patch",
        "0009-home-lazy-list-signal.patch",
        "0010-home-defer-optional-views.patch",
        "0011-frame-neighborhood-optional.patch",
    ]
    text = "\n".join(p.read_text() for p in patches[-7:])
    assert "CellRendererFavorite" in text
    assert "supported_prefixes" in text
    assert "_ensure_group_box" in text
    assert "Neighborhood unavailable for FriendsTray" in text
