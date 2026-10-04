import subprocess
from pathlib import Path


ROOT = Path(__file__).parents[1]
GATE = ROOT / "scripts/sugar-gtk4-retirement-gate.sh"


def test_retirement_gate_is_non_destructive_and_honest_about_open_work():
    source = GATE.read_text()
    assert "rm -rf" not in source
    assert "GTK3 fallback/reference packages remain installed." in source

    result = subprocess.run(["bash", str(GATE)], capture_output=True, text=True)
    assert result.returncode == 1
    assert "gtk4-retirement=BLOCKED" in result.stdout
    assert "blocker=full-parity" in result.stdout
    assert "blocker=collaboration-join" in result.stdout
    assert "blocker=shell-session-restart" not in result.stdout
