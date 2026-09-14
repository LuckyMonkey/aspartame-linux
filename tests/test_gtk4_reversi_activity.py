from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_reversi_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-reversi-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "reversiactivity4.py").read_text()
    assert "bundle_id = net.coderanger.olpc.reversi" in info
    assert "class ReversiActivity(SimpleActivity)" in source
    assert "def _moves" in source and "def _play" in source
    assert "Game over" in source and "not self._moves(3 - self.player)" in source
    assert "net.coderanger.olpc.reversi" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
