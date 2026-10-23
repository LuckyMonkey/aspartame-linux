import subprocess
from pathlib import Path


ROOT = Path(__file__).parents[1]
GATE = ROOT / "scripts/sugar-gtk4-retirement-gate.sh"


def test_retirement_gate_is_non_destructive():
    source = GATE.read_text()
    assert "rm -rf" not in source and "pacman" not in source
    assert "GTK3 fallback/reference packages remain installed." in source
    assert "build a disposable image before removal" in source


def test_gate_passes_once_every_candidate_is_full_port():
    # All seven candidates passed packaged-ISO receipts on 2026-10-23
    # (reports/gtk4/fullport-receipts-20261023.md).
    result = subprocess.run(["bash", str(GATE)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout
    assert "gtk4-retirement=PASS" in result.stdout
    assert '"Color My World"' not in GATE.read_text().split("retirement_candidates=(")[1].split(")")[0]


def test_gate_blocks_when_a_candidate_is_not_full_port(tmp_path):
    # Copy the repository layout the gate reads, with one row demoted.
    for rel in ("scripts/sugar-gtk4-retirement-gate.sh",
                "reports/gtk4/share-join-qualification-20261004.md",
                "reports/gtk4/chirality-session-resume-implementation-20261004.md"):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text((ROOT / rel).read_text())
    doc = "docs/sugar-modernization/ACTIVITY_PORT_CLASSIFICATION.md"
    (tmp_path / doc).parent.mkdir(parents=True)
    (tmp_path / doc).write_text((ROOT / doc).read_text().replace("| Abacus | FULL PORT |", "| Abacus | FUNCTIONAL PORT |"))
    result = subprocess.run(["bash", str(tmp_path / "scripts/sugar-gtk4-retirement-gate.sh")],
                            capture_output=True, text=True)
    assert result.returncode == 1
    assert "blocker=full-parity" in result.stdout and "missing-full-parity=Abacus" in result.stdout
