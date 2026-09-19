from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_switching_probe_covers_home_frame_home_return_path():
    script = (ROOT / 'scripts/sugar-gtk4-switching-probe.py').read_text()
    assert 'shell.ShowHome()' in script
    assert 'shell.ShowFrame()' in script
    assert 'switching-probe=PASS' in script
    assert 'MODERN_ATSPI_BUS' in script
