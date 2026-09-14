from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_blockparty_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-blockparty-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "blockpartyactivity4.py").read_text()
    assert "bundle_id = org.laptop.BlockPartyActivity" in info
    assert "sugar-activity4 blockpartyactivity4.BlockPartyActivity" in info
    assert "class BlockPartyActivity(SimpleActivity)" in source
    assert "Reset puzzle" in source
    assert "org.laptop.BlockPartyActivity" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-blockparty-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-blockparty-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
