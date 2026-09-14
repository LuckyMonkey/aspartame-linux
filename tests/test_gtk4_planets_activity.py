from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_planets_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-planets-activity"
    info = (package / "activity/activity.info").read_text(); source = (package / "planetsactivity4.py").read_text()
    assert "bundle_id = org.sugarlabs.Planets" in info
    assert "sugar-activity4 planetsactivity4.PlanetsActivity" in info
    assert "class PlanetsActivity(SimpleActivity)" in source
    assert "set_draw_func" in source and "Earth" in source
    assert "org.sugarlabs.Planets" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-planets-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-planets-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
