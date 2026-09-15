from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_modern_runner_serializes_casilda_session_ownership():
    runner = (ROOT / "scripts/sugar-gtk4-run.sh").read_text()
    assert 'session_lock="$runroot/gtk4-session.lock"' in runner
    assert 'flock -n 9' in runner
    assert "already running" in runner
    assert 'ASPARTAME_GTK4_LOG="$log"' in runner
    assert 'exec > >(tee -a "$log") 2>&1' in runner


def test_runtime_check_uses_the_active_shell_log():
    checker = (ROOT / "scripts/sugar-gtk4-runtime-check.sh").read_text()
    assert "ASPARTAME_GTK4_LOG=" in checker
    assert "session_log" in checker
