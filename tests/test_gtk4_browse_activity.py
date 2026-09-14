from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_build_stages_pinned_gtk4_browse_activity():
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    init = (ROOT / "scripts/sugar-gtk4-init.sh").read_text()
    assert 'browse_activity="$root/sources/browse-activity"' in build
    assert 'ln -sfn "$browse_activity" "$activity_dir/Browse.activity"' in build
    assert "browse-activity|https://github.com/Inuth0603/browse-activity" in init
