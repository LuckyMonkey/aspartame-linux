from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_connect_the_dots_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-connect-the-dots-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "connectthedotsactivity4.py").read_text()
    assert "bundle_id = org.sugarlabs.ConnectTheDots" in info
    assert "sugar-activity4 connectthedotsactivity4.ConnectTheDotsActivity" in info
    assert "class ConnectTheDotsActivity(SimpleActivity)" in source
    assert "Puzzle complete!" in source
    assert "def read_file(self, file_path)" in source
    assert '"connected": self._connected' in source
    matrix = (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    sync = (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert "org.sugarlabs.ConnectTheDots" in matrix
    assert "gtk4-connect-the-dots-activity" in sync
    assert "gtk4-connect-the-dots-activity" in build
