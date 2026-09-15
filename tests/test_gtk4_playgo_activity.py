from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_playgo_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-playgo-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "playgoactivity4.py").read_text()
    assert "bundle_id = org.laptop.PlayGo" in info
    assert "sugar-activity4 playgoactivity4.PlayGoActivity" in info
    assert "class PlayGoActivity(SimpleActivity)" in source
    assert "New game" in source
    assert "def read_file" in source and "def write_file" in source
    assert "org.laptop.PlayGo" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-playgo-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-playgo-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
