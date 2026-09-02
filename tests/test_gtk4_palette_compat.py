from pathlib import Path

ROOT = Path(__file__).parents[1]

def test_palette_menu_item_compatibility_patch_maps_old_calls_to_gtk4_image_api():
    patch = (ROOT / "patches/gtk4-preview/0013-toolkit-palette-icon-compat.patch").read_text()
    assert "def set_icon_widget(self, icon):" in patch
    assert "self.set_image(icon)" in patch

def test_gtk4_build_applies_palette_compatibility_to_toolkit():
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert "*0013*|*0015*|*0016*|*0017*) target=\"$toolkit\"" in build


def test_cell_renderer_props_compatibility_patch_targets_toolkit_boundary():
    patch = (ROOT / "patches/gtk4-preview/0015-toolkit-cell-renderer-props-compat.patch").read_text()
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert "class _CellRendererIconProps" in patch
    assert "self.props = _CellRendererIconProps(self)" in patch
    assert "def connect(self, signal_name, callback, *user_data):" in patch
    assert "*0015*|*0016*|*0017*) target=\"$toolkit\"" in build


def test_gtk4_cell_renderer_uses_native_gobject_boundary():
    patch = (ROOT / "patches/gtk4-preview/0016-toolkit-cell-renderer-gobject.patch").read_text()
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert "class CellRendererIcon(Gtk.CellRenderer):" in patch
    assert "do_snapshot(self, snapshot, widget, background_area, cell_area, flags)" in patch
    assert "*0016*|*0017*) target=\"$toolkit\"" in build


def test_gtk4_icon_file_alias_is_staged_after_renderer_patch():
    patch = (ROOT / "patches/gtk4-preview/0017-toolkit-icon-file-alias.patch").read_text()
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert "file = GObject.Property" in patch
    assert "0017*) target=\"$toolkit\"" in build


def test_gtk4_build_stages_and_launcher_starts_datastore_preview():
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    run = (ROOT / "scripts/sugar-gtk4-run.sh").read_text()
    session = (ROOT / "scripts/sugar-gtk4-session.sh").read_text()
    assert "0014*) target=\"$root/sources/sugar-datastore\"" in build
    assert "python_version=$($venv/bin/python" in build
    assert "metadatareader$python_ext_suffix" in build
    assert "metadata_reader=$(find" in run
    assert "-name 'metadatareader*.so'" in run
    assert "org.laptop.sugar.DataStore" in session
