from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_ballandbrick_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-ballandbrick-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "ballandbrickactivity4.py").read_text()
    assert "bundle_id = org.sugarlabs.BallAndBrick" in info
    assert "sugar-activity4 ballandbrickactivity4.BallAndBrickActivity" in info
    assert "class BallAndBrickActivity(SimpleActivity)" in source
    assert "Reset game" in source
    assert "org.sugarlabs.BallAndBrick" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-ballandbrick-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-ballandbrick-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
