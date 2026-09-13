from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_single_process_activity_activation_reuses_window():
    patch = (ROOT / "patches/gtk4-preview/0047-toolkit-single-process-activation-guard.patch").read_text()
    assert "_sugar_activity_instance" in patch
    assert "re-presenting existing Activity" in patch
    assert "app.add_window(activity)" in patch


def test_activity_activation_guard_is_routed_by_guest_build():
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert "*0047*) target=\"$toolkit\"" in build
    assert "*0048*|*0049*) target=\"$root/sources/sugar\"" in build
    assert '"$patch_name" == *0047*' in build


def test_qemu_key_helper_uses_bounded_hmp_symbolic_keycodes():
    helper = (ROOT / "scripts/qemu-send-key.py").read_text()
    assert 'sendkey {KEYCODES[key]} 100' in helper
    assert 'HMP' in helper


def test_zoom_keys_are_captured_at_the_gtk4_shell_window():
    patch = (ROOT / "patches/gtk4-preview/0048-main-zoom-key-capture.patch").read_text()
    for key in ("Gdk.KEY_F1", "Gdk.KEY_F2", "Gdk.KEY_F3", "Gdk.KEY_F4"):
        assert key in patch
    assert "Gtk.PropagationPhase.CAPTURE" in patch
    assert "_sugar_zoom_controller" in patch


def test_shell_exposes_semantic_journal_action():
    patch = (ROOT / "patches/gtk4-preview/0049-shell-show-journal-action.patch").read_text()
    assert "def ShowJournal" in patch
    assert "journal.show_journal()" in patch
    assert "model.ZOOM_ACTIVITY" in patch
