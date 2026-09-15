from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_mancala_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-mancala-activity"
    assert "bundle_id = mulawa.Mancala" in (package / "activity/activity.info").read_text()
    source = (package / "mancalaactivity4.py").read_text()
    assert "class MancalaActivity(SimpleActivity)" in source
    assert "self.pits" in source and "New game" in source
    assert "self._pit_index(pos)" in source
    assert "18 - board_position" in source
    assert "def read_file" in source and "def write_file" in source
    assert "mulawa.Mancala" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
