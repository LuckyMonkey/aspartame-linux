from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_build_stages_pinned_gtk4_image_viewer():
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert 'imageviewer_activity="$root/sources/imageviewer-activity"' in build
    assert 'ln -sfn "$imageviewer_activity" "$activity_dir/ImageViewer.activity"' in build
    init = (ROOT / "scripts/sugar-gtk4-init.sh").read_text()
    assert "imageviewer-activity|https://github.com/Inuth0603/imageviewer-activity" in init
