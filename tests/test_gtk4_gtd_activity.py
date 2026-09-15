from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_gtd_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-gtd-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "gtdactivity4.py").read_text()
    assert "bundle_id = org.sugarlabs.GTDActivity" in info
    assert "sugar-activity4 gtdactivity4.GTDActivity" in info
    assert "class GTDActivity(SimpleActivity)" in source
    assert "New task" in source
    assert "org.sugarlabs.GTDActivity" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-gtd-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-gtd-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()


def test_gtd_activity_has_journal_task_roundtrip():
    source = (ROOT / "packages/gtk4-gtd-activity/gtdactivity4.py").read_text()
    assert "def read_file(self, file_path)" in source
    assert "def write_file(self, file_path)" in source
    assert '"tasks"' in source
    assert '"done"' in source
