from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_diamond_fusion_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-diamond-fusion-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "diamondfusionactivity4.py").read_text()
    assert "bundle_id = com.francocorrea.diamondfusion" in info
    assert "sugar-activity4 diamondfusionactivity4.DiamondFusionActivity" in info
    assert "class DiamondFusionActivity(SimpleActivity)" in source
    assert "Gtk.GestureClick" in source and "Fused!" in source
    assert (package / "activity/diamond-fusion.svg").is_file()
    matrix = (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "com.francocorrea.diamondfusion|diamondfusionactivity4.DiamondFusionActivity" in matrix
    for path in ("scripts/sugar-gtk4-dev-sync.sh", "scripts/sugar-gtk4-build.sh"):
        assert "gtk4-diamond-fusion-activity" in (ROOT / path).read_text()
