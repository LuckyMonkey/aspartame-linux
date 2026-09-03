from pathlib import Path


ROOT = Path(__file__).parents[1]
MODULE = ROOT / 'archiso/aspartame/airootfs/usr/share/aspartame/aspartame_visual.py'


def test_visual_tokens_are_bounded_and_documented():
    source = MODULE.read_text(encoding='utf-8')
    assert 'XoColor' in source
    assert 'HELP_BUTTON_DIAMETER = 44' in source
    assert 'RATING_FACE_SIZE = 52' in source
    baseline = (ROOT / 'docs/design/SUGAR_VISUAL_BASELINE.md').read_text(encoding='utf-8')
    assert 'not a status bar' in baseline
    assert 'transparent native top-level compositing is not a requirement' in baseline
