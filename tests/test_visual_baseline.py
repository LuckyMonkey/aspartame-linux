from pathlib import Path


ROOT = Path(__file__).parents[1]
MODULE = ROOT / 'archiso/aspartame/airootfs/usr/share/aspartame/aspartame_visual.py'


def test_visual_tokens_are_bounded_and_documented():
    source = MODULE.read_text(encoding='utf-8')
    assert 'XoColor' in source
    assert 'HELP_BUTTON_DIAMETER = 32' in source
    assert 'RATING_FACE_SIZE = 52' in source
    baseline = (ROOT / 'docs/design/SUGAR_VISUAL_BASELINE.md').read_text(encoding='utf-8')
    assert 'not a status bar' in baseline
    assert 'transparent native top-level compositing is not a requirement' in baseline


def test_help_uses_canonical_activity_artwork():
    toolbar = (ROOT / 'sugar-overlay/src/jarabe/desktop/viewtoolbar.py').read_text(encoding='utf-8')
    assert 'Help.activity/activity/activity-help.svg' in toolbar
    assert "self.insert(help_toolitem, 2)" in toolbar
    assert "background: transparent;" in toolbar
