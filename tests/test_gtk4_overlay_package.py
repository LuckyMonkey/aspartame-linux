from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_desktop_overlay_extends_jarabe_package_path():
    init = ROOT / "gtk4-overlay/src/jarabe/desktop/__init__.py"
    source = init.read_text()
    assert "extend_path" in source
    assert "__path__ = extend_path" in source
