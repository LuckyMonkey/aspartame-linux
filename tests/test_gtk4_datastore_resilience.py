from pathlib import Path


ROOT = Path(__file__).parents[1]
PATCH = ROOT / "patches/gtk4-preview/0170-datastore-ignore-malformed-numeric-metadata.patch"


def test_datastore_patch_skips_only_malformed_numeric_metadata():
    source = PATCH.read_text()

    assert "dbus.Int32(value)" in source
    assert "for key, value in list(metadata.items())" in source
    assert "TypeError, ValueError, OverflowError" in source
    assert "del metadata[key]" in source
    assert "Ignoring malformed numeric metadata" in source


