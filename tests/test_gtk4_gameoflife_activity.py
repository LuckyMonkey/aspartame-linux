from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_gameoflife_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-gameoflife-activity"
    info = (package / "activity/activity.info").read_text(); source = (package / "gameoflifeactivity4.py").read_text()
    assert "bundle_id = org.sugarlabs.gameOfLife" in info
    assert "sugar-activity4 gameoflifeactivity4.GameOfLifeActivity" in info
    assert "class GameOfLifeActivity(SimpleActivity)" in source
    assert "neighbors" in source and 'label="Step"' in source
    assert "org.sugarlabs.gameOfLife" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-gameoflife-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-gameoflife-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
