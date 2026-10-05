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
    assert "Remove task" in source
    assert "Move task up" in source and "Move task down" in source
    assert "def _move_row(self, _button, row, delta)" in source
    assert "def _replace_rows(self, rows)" in source
    assert 'Gtk.Frame(label="Tasks")' in source
    assert 'No tasks yet. Add one above.' in source
    assert "get_row_at_index(index)" in source
    assert "def _task_rows(self)" in source
    assert "entry_row = Gtk.Box" in source and "set_vexpand(True)" in source
    assert "org.sugarlabs.GTDActivity" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-gtd-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-gtd-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()


def test_gtd_activity_has_journal_task_roundtrip():
    source = (ROOT / "packages/gtk4-gtd-activity/gtdactivity4.py").read_text()
    assert "def read_file(self, file_path)" in source
    assert "def write_file(self, file_path)" in source
    assert '"tasks"' in source
    assert '"done"' in source
    assert "row.task_check" in source


def test_gtd_roundtrip_exercises_remove_and_reorder_actions():
    probe = (ROOT / "scripts/sugar-gtk4-gtd-roundtrip.py").read_text()
    assert '"Move down"' in probe
    assert '"Remove task"' in probe
    assert '"Call the team", "done": False' in probe
