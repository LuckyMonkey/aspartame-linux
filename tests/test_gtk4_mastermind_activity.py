from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_mastermind_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-mastermind-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "mastermindactivity4.py").read_text()
    matrix = (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    run = (ROOT / "scripts/sugar-gtk4-run.sh").read_text()
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    sync = (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "bundle_id = org.laptop.Mastermind" in info
    assert "class MastermindActivity(SimpleActivity)" in source
    assert "Gtk.Button" in source and "Check code" in source
    assert "def read_file(self, file_path)" in source
    assert '"guesses": self.guesses' in source
    assert 'self.progress.set_text' in source
    assert "org.laptop.Mastermind" in matrix
    assert "Mastermind" in run and "Mastermind" in build and "gtk4-mastermind-activity" in sync
