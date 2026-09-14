from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_last_one_loses_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-last-one-loses-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "lolactivity4.py").read_text()
    assert "bundle_id = org.olpc-france.LOLActivity" in info
    assert "sugar-activity4 lolactivity4.LastOneLosesActivity" in info
    assert "class LastOneLosesActivity(SimpleActivity)" in source
    assert "Take 1–3" in source
    assert "org.olpc-france.LOLActivity" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-last-one-loses-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-last-one-loses-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
