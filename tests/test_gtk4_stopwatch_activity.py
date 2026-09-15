from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_stopwatch_exposes_a_journal_state_boundary():
    package = ROOT / "packages/gtk4-stopwatch-activity"
    source = next(package.glob("*activity4.py")).read_text()
    assert "def read_file(self, file_path)" in source
    assert "def write_file(self, file_path)" in source
    assert 'json.dumps({"elapsed": self.elapsed}' in source


def test_stopwatch_roundtrip_probe_targets_journal_resume():
    probe = (ROOT / "scripts/sugar-gtk4-stopwatch-roundtrip.py").read_text()
    assert 'BUNDLE_ID = "org.sugarlabs.StopwatchActivity"' in probe
    assert 'PROCESS_MARKER = "stopwatchactivity4.StopwatchActivity"' in probe
    assert 'expected_text in visible_text' in probe
    assert 'journal.LaunchBundle(BUNDLE_ID, object_id)' in probe
    assert 'json.dumps({"elapsed": elapsed}' in probe
    assert "stopwatch-roundtrip=PASS" in probe
