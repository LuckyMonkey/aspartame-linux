from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_stopwatch_exposes_a_journal_state_boundary():
    package = ROOT / "packages/gtk4-stopwatch-activity"
    source = next(package.glob("*activity4.py")).read_text()
    assert "def read_file(self, file_path)" in source
    assert "def write_file(self, file_path)" in source
    assert 'json.dumps({"elapsed": self.elapsed}' in source
