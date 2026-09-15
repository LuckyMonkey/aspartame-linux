from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_modern_runner_serializes_casilda_session_ownership():
    runner = (ROOT / "scripts/sugar-gtk4-run.sh").read_text()
    assert 'session_lock="$runroot/gtk4-session.lock"' in runner
    assert 'flock -n 9' in runner
    assert "already running" in runner
