from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_build_stages_native_gtk4_browse_activity():
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    init = (ROOT / "scripts/sugar-gtk4-init.sh").read_text()
    assert 'browse_activity="$root/sources/browse-activity"' in build
    assert 'native_browse_activity="$repo/packages/gtk4-browse-activity"' in build
    assert 'ln -sfn "$native_browse_activity" "$activity_dir/Browse.activity"' in build
    source = (ROOT / "packages/gtk4-browse-activity/browseactivity4.py").read_text()
    assert "class BrowseActivity(SimpleActivity)" in source
    assert "urllib.request.urlopen" in source
    assert "Gtk.TextView" in source
    assert "browse-activity|https://github.com/Inuth0603/browse-activity" in init
    packages = (ROOT / "archiso/aspartame/packages.x86_64").read_text()
    assert "webkitgtk-6.0" in packages
    assert "vte4" in packages
    # Browse and Terminal use native GTK4 surfaces; retired VTE/WebKit
    # previews must not block the modern guest build.
    assert "vte-2.91-gtk4 >= 0.84" not in build
    assert "webkitgtk-6.0 >= 2.50" not in build
