from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_controlpanel_requests_full_monitor_geometry():
    patch = (ROOT / 'patches/gtk4-preview/folded/'
             '0167-controlpanel-use-full-monitor-geometry.patch').read_text()
    assert 'width = sw' in patch
    assert 'height = sh' in patch
    assert 'width = sw - offset * 2' in patch


