from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_abacus_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-abacus-activity"
    info = (package / "activity/activity.info").read_text(); source = (package / "abacusactivity4.py").read_text()
    assert "bundle_id = com.homegrownapps.abacus" in info
    assert "sugar-activity4 abacusactivity4.AbacusActivity" in info
    assert "class AbacusActivity(SimpleActivity)" in source
    assert "place value" in source and 'label="Clear"' in source
    assert "com.homegrownapps.abacus" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-abacus-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-abacus-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
