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
    assert "blocker=collaboration-join" not in result.stdout  # qualified 2026-10-22
    assert "blocker=shell-session-restart" not in result.stdout
    # Markdown and Pippy passed core-workflow receipts on 2026-10-22.
    assert "missing-full-parity=Portfolio,Finance,Write,Jukebox,Color My World,Abacus" in result.stdout
    assert "evidence-share=reports/gtk4/share-join-qualification-20261004.md" in result.stdout
    assert "evidence-chirality=reports/gtk4/chirality-session-resume-implementation-20261004.md" in result.stdout
