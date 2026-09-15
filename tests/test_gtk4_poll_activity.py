from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_poll_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-poll-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "pollactivity4.py").read_text()
    assert "bundle_id = org.worldwideworkshop.PollBuilder" in info
    assert "class PollActivity(SimpleActivity)" in source
    assert "self.votes" in source and "Vote" in source
    assert "def read_file" in source and "def write_file" in source
    assert "org.worldwideworkshop.PollBuilder" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
