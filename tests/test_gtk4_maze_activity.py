from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_maze_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-maze-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "mazeactivity4.py").read_text()
    assert "bundle_id = vu.lux.olpc.Maze" in info
    assert "sugar-activity4 mazeactivity4.MazeActivity" in info
    assert "class MazeActivity(SimpleActivity)" in source
    assert "New maze" in source
    assert "def read_file" in source and "def write_file" in source
    assert "vu.lux.olpc.Maze" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-maze-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-maze-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
