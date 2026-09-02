from pathlib import Path

ROOT = Path(__file__).parents[1]

def test_palette_menu_item_compatibility_patch_maps_old_calls_to_gtk4_image_api():
    patch = (ROOT / "patches/gtk4-preview/0013-toolkit-palette-icon-compat.patch").read_text()
    assert "def set_icon_widget(self, icon):" in patch
    assert "self.set_image(icon)" in patch

def test_gtk4_build_applies_palette_compatibility_to_toolkit():
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert "*0013*) target=\"$toolkit\"" in build


def test_gtk4_build_stages_and_launcher_starts_datastore_preview():
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    run = (ROOT / "scripts/sugar-gtk4-run.sh").read_text()
    session = (ROOT / "scripts/sugar-gtk4-session.sh").read_text()
    assert "0014*) target=\"$root/sources/sugar-datastore\"" in build
    assert "carquinyol/metadatareader.cpython-312-x86_64-linux-gnu.so" in run
    assert "org.laptop.sugar.DataStore" in session
