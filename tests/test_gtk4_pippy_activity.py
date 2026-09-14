from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_pippy_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-pippy-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "pippyactivity4.py").read_text()
    assert "bundle_id = org.laptop.Pippy" in info
    assert "sugar-activity4 pippyactivity4.PippyActivity" in info
    assert "class PippyActivity(SimpleActivity)" in source
    assert 'label="Run"' in source and "Program output" in source
    assert "subprocess.run" in source and '"-I"' in source
    matrix = (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "org.laptop.Pippy|pippyactivity4.PippyActivity" in matrix
    for script in ("sugar-gtk4-dev-sync.sh", "sugar-gtk4-build.sh"):
        assert "gtk4-pippy-activity" in (ROOT / "scripts" / script).read_text()
