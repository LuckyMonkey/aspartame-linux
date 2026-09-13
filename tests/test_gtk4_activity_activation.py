from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_single_process_activity_activation_reuses_window():
    patch = (ROOT / "patches/gtk4-preview/0047-toolkit-single-process-activation-guard.patch").read_text()
    assert "_sugar_activity_instance" in patch
    assert "re-presenting existing Activity" in patch
    assert "app.add_window(activity)" in patch


def test_activity_activation_guard_is_routed_by_guest_build():
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert "*0047*" in build and "target=\"$toolkit\"" in build
    assert '*0048*' in build and '*0057*' in build
    assert '"$patch_name" == *0047*' in build


def test_qemu_key_helper_uses_bounded_hmp_symbolic_keycodes():
    helper = (ROOT / "scripts/qemu-send-key.py").read_text()
    assert 'sendkey {KEYCODES[key]} 100' in helper
    assert 'HMP' in helper
    assert 'def _read_prompt' in helper
    assert '_read_prompt(sock)' in helper


def test_qemu_pointer_helper_uses_absolute_tablet_events():
    helper = (ROOT / "scripts/qemu-send-pointer.py").read_text()
    assert 'input-send-event' in helper
    assert '"type": "abs"' in helper
    assert '"type": "btn"' in helper
    assert 'initial greeting' in helper


def test_qemu_key_helper_supports_activity_text_input():
    helper = (ROOT / "scripts/qemu-send-key.py").read_text()
    assert 'KEYCODES.update' in helper
    assert 'or A..Z' in helper


def test_zoom_keys_are_captured_at_the_gtk4_shell_window():
    patch = (ROOT / "patches/gtk4-preview/0048-main-zoom-key-capture.patch").read_text()
    for key in ("Gdk.KEY_F1", "Gdk.KEY_F2", "Gdk.KEY_F3", "Gdk.KEY_F4"):
        assert key in patch
    assert "Gtk.PropagationPhase.CAPTURE" in patch
    assert "_sugar_zoom_controller" in patch
    assert "set_focus(shell_instance._overlay)" in patch
    assert "Gdk.KEY_F5" not in patch


def test_frame_and_journal_keys_are_captured_by_gtk4_shell():
    patch = (ROOT / "patches/gtk4-preview/0050-main-frame-journal-key-capture.patch").read_text()
    assert "Gdk.KEY_F5" in patch
    assert "Gdk.KEY_F6" in patch
    assert "notify_key_press()" in patch
    assert "journalactivity.get_journal().show_journal()" in patch


def test_gtk4_overlay_focus_patch_is_routed():
    patch = (ROOT / "patches/gtk4-preview/0051-main-focus-overlay.patch").read_text()
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert "set_focus(shell_instance._overlay)" in patch
    assert "*0051*" in build


def test_shell_exposes_semantic_frame_action():
    patch = (ROOT / "patches/gtk4-preview/0052-shell-show-frame-action.patch").read_text()
    assert "def ShowFrame" in patch
    assert "frame.get_view().show()" in patch


def test_focus_overlay_final_patch_is_idempotent():
    patch = (ROOT / "patches/gtk4-preview/0054-main-focus-overlay-final.patch").read_text()
    assert "set_focus(shell_instance._overlay)" in patch


def test_empty_collaboration_state_is_routed_into_guest_sugar():
    patch = (ROOT / "patches/gtk4-preview/0055-empty-space-view-state.patch").read_text()
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert "No friends are nearby yet." in patch
    assert '*0055*' in build and 'target="$root/sources/sugar"' in build
    assert '"$patch_name" == *0055*' in build


def test_control_panel_can_open_without_active_activity():
    patch = (ROOT / "patches/gtk4-preview/0057-controlpanel-home-owner.patch").read_text()
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert "if activity is not None" in patch
    assert "panel.set_transient_for(shell_model._main_window)" in patch
    assert "*0057*" in build and 'target="$root/sources/sugar"' in build


def test_shell_exposes_semantic_control_panel_action():
    patch = (ROOT / "patches/gtk4-preview/0058-shell-show-controlpanel-action.patch").read_text()
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert "def ShowControlPanel" in patch
    assert "ControlPanel(0)" in patch
    assert "getattr(self._shell_model, '_main_window', None)" in patch
    assert "*0058*" in build


def test_native_help_activity_is_staged_for_modern_space():
    info = (ROOT / "packages/gtk4-help-activity/activity/activity.info").read_text()
    source = (ROOT / "packages/gtk4-help-activity/helpactivity4.py").read_text()
    assert (ROOT / "packages/gtk4-help-activity/activity/activity-help.svg").is_file()
    run = (ROOT / "scripts/sugar-gtk4-run.sh").read_text()
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert "exec = sugar-activity4 helpactivity4.HelpActivity" in info
    assert "from sugar4.activity import SimpleActivity" in source
    assert "def __init__(self, activity_handle=None)" in source
    assert 'search.set_placeholder_text("Search help")' in source
    assert 'search.connect("changed", _search_changed)' in source
    assert 'input_status.set_text' in source
    assert 'root.add_css_class("help-root")' in source
    assert 'provider.load_from_data' in source
    assert 'Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION' in source
    launcher = (ROOT / "packages/gtk4-help-activity/bin/sugar-activity4").read_text()
    assert "export ASPARTAME_GTK4_PREVIEW=1" in launcher
    assert "Help.activity/activity/activity.info" in run
    assert 'ln -sfn "$help_activity" "$activity_dir/Help.activity"' in build


def test_shell_stop_activity_is_authoritative_and_terminates_child():
    stop = (ROOT / "patches/gtk4-preview/0062-shell-stop-activity-action.patch").read_text()
    terminate = (ROOT / "patches/gtk4-preview/0064-shell-stop-activity-terminates-process.patch").read_text()
    fallback = (ROOT / "patches/gtk4-preview/0065-shell-stop-activity-pid-fallback.patch").read_text()
    assert "def StopActivity(self, activity_id)" in stop
    assert "get_activity_by_id" in stop
    assert "os.kill(pid, 15)" in terminate
    assert "activity_id.encode()" in fallback


def test_child_exit_notifies_shell_without_self_dbus_roundtrip():
    patch = (ROOT / "patches/gtk4-preview/0066-toolkit-local-launch-failure-notify.patch").read_text()
    assert "shell.get_model().notify_launch_failed(activity_id)" in patch
    assert "+        dbus.Interface(shell" not in patch


def test_activity_removal_is_idempotent_in_shell_and_frame():
    patch = (ROOT / "patches/gtk4-preview/0067-shell-idempotent-activity-removal.patch").read_text()
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert "self._buttons.pop(home_activity, None)" in patch
    assert "home_activity not in self._activities" in patch
    assert "*0067*" in build


def test_gtk4_menuitem_preserves_sugar_set_image_api():
    patch = (ROOT / "patches/gtk4-preview/0068-toolkit-menuitem-set-image.patch").read_text()
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert "def set_image(self, image)" in patch
    assert "self._content_box.prepend(image)" in patch
    assert "*0068*" in build


def test_group_view_imports_gettext_for_empty_state():
    patch = (ROOT / "patches/gtk4-preview/0069-groupbox-gettext-import.patch").read_text()
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert "from gettext import gettext as _" in patch
    assert "*0069*" in build


def test_compositor_key_capture_patch_is_routed():
    patch = (ROOT / "patches/gtk4-preview/0070-main-compositor-key-capture.patch").read_text()
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert "shell_instance.compositor.add_controller(activity_keys)" in patch
    assert "Gtk.PropagationPhase.CAPTURE" in patch
    assert "*0070*" in build


def test_zoom_shortcuts_dismiss_frame_overlay():
    patch = (ROOT / "patches/gtk4-preview/0071-main-zoom-hides-frame.patch").read_text()
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert "frame.get_view().hide()" in patch
    assert "*0071*" in build


def test_shell_exposes_semantic_journal_action():
    patch = (ROOT / "patches/gtk4-preview/0049-shell-show-journal-action.patch").read_text()
    assert "def ShowJournal" in patch
    assert "journal.show_journal()" in patch
    assert "model.ZOOM_ACTIVITY" in patch
