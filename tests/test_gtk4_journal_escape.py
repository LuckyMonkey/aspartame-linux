from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_journal_escape_controller_captures_focused_children():
    patch = (ROOT / "patches/gtk4-preview/0133-journal-capture-escape.patch").read_text()
    assert "journalactivity.py" in patch
    assert "set_propagation_phase(Gtk.PropagationPhase.CAPTURE)" in patch
    assert "Escape" in patch
