from pathlib import Path


ROOT = Path(__file__).parents[1]
MODERNIZATION = ROOT / "docs/sugar-modernization"


def test_activity_port_runbook_covers_lifecycle_proof_gates():
    runbook = (MODERNIZATION / "GTK4_ACTIVITY_RUNBOOK.md").read_text()

    for marker in (
        "Activity D-Bus lifecycle contract",
        "private Wayland client surface appears",
        "canonical Stop action",
        "bus-name release and process exit",
        "relaunch/resume evidence",
    ):
        assert marker in runbook


def test_gtk4_runbooks_use_the_complete_preview_root():
    smoke = (MODERNIZATION / "GTK4_RUNBOOK.md").read_text()
    bootstrap = (MODERNIZATION / "GTK4_BOOTSTRAP.md").read_text()

    assert 'GTK4_ROOT="$MODERNIZATION_ROOT" make sugar-gtk4-smoke' in smoke
    assert 'GTK4_ROOT="$MODERNIZATION_ROOT/sugar-toolkit-gtk4"' not in smoke
    assert "/home/aspartame/Development/gtk4-preview" in bootstrap


def test_status_does_not_reference_a_missing_blocker_document():
    status = (MODERNIZATION / "GTK4_BOOTSTRAP.md").read_text()

    assert "BLOCKERS.md" not in status
    assert "shell-mediated Activity launch/stop are verified" in status
    assert "pointer/keyboard/focus" in status
