from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_spaces_controller_uses_existing_metacity_workspaces():
    controller = (ROOT / 'scripts/sugar-gtk4-space.sh').read_text()
    assert 'switch-to-workspace-1' in controller
    assert 'switch-to-workspace-2' in controller
    assert 'F9' in controller
    assert 'F10' in controller
    assert 'sugar-gtk4-run.sh' in controller
    assert 'SUGAR_WINDOWED=0' in controller
    assert 'place --pid' in controller
    assert 'gtk3_pid()' in controller
    assert 'dead session bus' in controller
    assert 'DBUS_SESSION_BUS_ADDRESS=unix:path=' in controller
    assert '[ -S "$bus_address" ]' in controller
    assert 'retire_stale_gtk4()' in controller
    assert 'Retiring stale GTK4 shell PID' in controller
    assert 'kill "$pid"' in controller
    assert 'org.freedesktop.DBus.Peer.Ping' in controller
    assert 'timeout 2 dbus-send' in controller
    assert 'python3 -m jarabe' in controller
    assert '--workspace 0' in controller
    assert '--workspace 1 --fullscreen' in controller
    assert 'activate --pid' in controller
    assert 'GTK3_PID' in controller
    assert 'GTK4_PID' in controller
    assert 'select_gtk3' in controller
    assert 'select_gtk4' in controller
    assert 'pgrep -u' in controller
    assert 'DBUS_SESSION_BUS_ADDRESS=*) export' in controller
    assert 'keybindings unavailable' in controller
    assert 'wmctrl' not in controller
    assert 'xdotool' not in controller


def test_standalone_session_exports_the_resolved_space_switcher():
    session = (ROOT / 'archiso/aspartame/airootfs/usr/local/bin/'
               'aspartame-x-session').read_text()
    assert 'gtk4_root=${ASPARTAME_GTK4_ROOT:-/usr/lib/aspartame/gtk4-preview}' in session
    assert 'gtk4_space="$gtk4_root/scripts/sugar-gtk4-space.sh"' in session
    assert 'export ASPARTAME_SPACE_SWITCHER="$gtk4_space"' in session


def test_direct_modern_runner_exports_its_space_switcher():
    runner = (ROOT / 'scripts/sugar-gtk4-run.sh').read_text()
    assert 'ASPARTAME_SPACE_SWITCHER="${ASPARTAME_SPACE_SWITCHER:-$project_root/scripts/sugar-gtk4-space.sh}"' in runner


def test_classic_keyhandler_keeps_f9_return_grab_for_modern_space():
    handler = (ROOT / 'sugar-overlay/src/jarabe/view/keyhandler.py').read_text()
    assert 'SugarExt.KeyGrabber' in handler
    assert 'get_active_workspace' in handler
    assert 'self._key_grabber.grab_keys(keys)' in handler
    assert 'workspace == 0' in handler
    assert 'Spaces key ownership' in handler
    assert 'self._key_grabber.grab_keys(["F9", "F10"])' in handler
    assert 'SugarExt.KeyGrabber()' in handler
    assert 'for space_key in ("F9", "F10")' in handler
    assert '_actions_table.setdefault("F9"' in handler
    assert '_actions_table.setdefault("F10"' in handler
    assert 'site-packages' in handler
    assert 'loader recurses' in handler


def test_x11_helper_uses_standard_ewmh_messages():
    helper = (ROOT / 'scripts/sugar-x11-workspace.py').read_text()
    assert '_NET_CURRENT_DESKTOP' in helper
    assert '_NET_WM_DESKTOP' in helper
    assert '_NET_ACTIVE_WINDOW' in helper
    assert '_NET_WM_STATE_FULLSCREEN' in helper
    assert 'SUBSTRUCTURE_REDIRECT_MASK' in helper
    assert 'XSendEvent' in helper
    assert 'actions.add_parser("activate")' in helper
    assert 'ewmh.activate(window)' in helper


def test_activate_sends_pager_request_to_target_window():
    import importlib.util

    helper_path = ROOT / "scripts/sugar-x11-workspace.py"
    spec = importlib.util.spec_from_file_location("sugar_x11_workspace", helper_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    messages = []
    ewmh = object.__new__(module.Ewmh)
    ewmh._send = lambda window, name, values: messages.append(
        (window, name, values)
    )

    ewmh.activate(0x1234)

    assert messages == [(0x1234, "_NET_ACTIVE_WINDOW", [2, 0, 0])]


def test_gtk4_main_window_routes_sugar_function_keys():
    # The zoom capture now arrives through the consolidated main.py patch.
    # Assert the end state rather than the patch that first introduced it:
    # 0090 corrected the setter to go through ShellModel.
    patch = (ROOT / "patches/gtk4-preview/0157-main-shell-window-consolidated.patch").read_text()
    assert "Gtk.EventControllerKey()" in patch
    assert "Gtk.PropagationPhase.CAPTURE" in patch
    for key in ("Gdk.KEY_F1", "Gdk.KEY_F2", "Gdk.KEY_F3", "Gdk.KEY_F4"):
        assert key in patch
    assert "shell_instance.get_model().set_zoom_level(level)" in patch
    assert "shell_instance.set_zoom_level(level)" not in patch


def test_gtk4_main_window_falls_back_to_semantic_space_actions():
    patch = (ROOT / "patches/gtk4-preview/0157-main-shell-window-consolidated.patch").read_text()
    assert "space_keys = (Gdk.KEY_F9, Gdk.KEY_F10)" in patch
    assert "semantic_keys._key_pressed_cb" in patch
    assert "Gdk.KEY_F9, Gdk.KEY_F10" in patch


def test_gtk4_space_keys_are_owned_by_the_shell_key_handler():
    # 0153 moved the action ownership into the shell key handler. The
    # consolidated main window has only a delivery fallback for startup/focus
    # races and delegates back to that same handler.
    keys = (ROOT / "patches/gtk4-preview/"
            "0153-shell-space-keys-work-from-every-window.patch").read_text()
    main = (ROOT / "patches/gtk4-preview/"
            "0157-main-shell-window-consolidated.patch").read_text()
    assert "ASPARTAME_SPACE_SWITCHER" in keys
    assert "subprocess.Popen" in keys
    assert "'F9': 'space_classic'," in keys
    assert "'F10': 'space_modern'," in keys
    assert "semantic_keys._key_pressed_cb" in main


def test_gtk4_runner_rejects_system_journal_window_import():
    runner = (ROOT / "scripts/sugar-gtk4-run.sh").read_text()
    assert "GTK4 Journal window resolved outside preview sources" in runner
    assert "preview_pythonpath" in runner
    assert "jarabe.journal.journalwindow" in runner


def test_no_preview_patch_reintroduces_the_sugarext_global_grabber():
    # 0094 installed a SugarExt.KeyGrabber in the modern shell and 0111
    # removed it again because the GIR lacks the API. Both are folded away;
    # what must stay true is that nothing puts it back.
    offenders = [
        path.name
        for path in (ROOT / "patches/gtk4-preview").glob("*.patch")
        if "SugarExt.KeyGrabber" in path.read_text(errors="ignore")
    ]
    assert offenders == [], offenders


def test_mesh_empty_state_and_drift_guards_are_present():
    patch = (ROOT / 'patches/gtk4-preview/0097-mesh-empty-state.patch').read_text()
    build = (ROOT / 'scripts/sugar-gtk4-build.sh').read_text()
    assert 'No people or shared Activities are nearby yet.' in patch
    assert '_empty_state' in patch
    assert 'existing idempotent Activity removal' in build
    assert 'existing Group view gettext import' in build


def test_neighborhood_accessibility_patch_is_routed():
    patch = (ROOT / 'patches/gtk4-preview/0114-neighborhood-accessibility.patch').read_text()
    build = (ROOT / 'scripts/sugar-gtk4-build.sh').read_text()
    assert "AccessibleProperty.LABEL" in patch
    assert "AccessibleRole.GROUP" in patch
    assert '*0114*) target="$root/sources/sugar" ;;' in build
    assert '*0115*) target="$root/sources/sugar" ;;' in build


def test_neighborhood_accessibility_order_patch_is_retired_after_fold():
    assert not (ROOT / 'patches/gtk4-preview/0127-neighborhood-accessibility-order.patch').exists()
    build = (ROOT / 'scripts/sugar-gtk4-build.sh').read_text()
    assert '*0127*) target="$root/sources/sugar" ;;' not in build


def test_zoom_service_dedupe_patch_is_retired_after_navigation_fold():
    assert not (ROOT / 'patches/gtk4-preview/0128-service-dedupe-zoom-actions.patch').exists()
    build = (ROOT / 'scripts/sugar-gtk4-build.sh').read_text()
    assert '*0128*) target="$root/sources/sugar" ;;' not in build


def test_journal_rooted_unparented_attach_patch_is_routed():
    patch = (ROOT / 'patches/gtk4-preview/0129-journal-rooted-unparented-attach.patch').read_text()
    build = (ROOT / 'scripts/sugar-gtk4-build.sh').read_text()
    assert 'blank page' in patch
    assert 'get_parent() is not None and widget.get_root() is not None' in patch
    assert '*0129*) target="$root/sources/sugar" ;;' in build


def test_journal_show_action_stack_visibility_patches_are_routed():
    build = (ROOT / 'scripts/sugar-gtk4-build.sh').read_text()
    for number, marker in (
            ('0130', 'model.stack.set_visible_child_name("journal")'),
            ('0131', 'journal.set_hexpand(True)'),
            ('0132', 'journal._canvas_area.set_visible(True)')):
        patch = next((ROOT / 'patches/gtk4-preview').glob(f'{number}-*.patch')).read_text()
        assert marker in patch
        assert f'*{number}*) target="$root/sources/sugar" ;;' in build


def test_group_accessibility_patch_is_routed():
    patch = (ROOT / 'patches/gtk4-preview/0116-group-accessibility.patch').read_text()
    build = (ROOT / 'scripts/sugar-gtk4-build.sh').read_text()
    assert "AccessibleProperty.LABEL" in patch
    assert "AccessibleRole.GROUP" in patch
    assert "[_('Group')]" in patch
    assert '*0116*) target="$root/sources/sugar" ;;' in build
    assert '*0117*) target="$root/sources/sugar" ;;' in build


def test_frame_accessibility_patch_is_routed():
    patch = (ROOT / 'patches/gtk4-preview/0118-frame-accessibility.patch').read_text()
    build = (ROOT / 'scripts/sugar-gtk4-build.sh').read_text()
    assert "[_('Frame')]" in patch
    assert "AccessibleRole.GROUP" in patch
    assert '*0118*) target="$root/sources/sugar" ;;' in build
    assert '*0119*) target="$root/sources/sugar" ;;' in build
    assert '*0120*) target="$root/sources/sugar" ;;' in build
    assert not (ROOT / 'patches/gtk4-preview/0121-frame-accessibility-final-placement.patch').exists()
    assert not (ROOT / 'patches/gtk4-preview/0122-frame-accessibility-relocate-final.patch').exists()
    assert not (ROOT / 'patches/gtk4-preview/0123-frame-accessibility-relocate-current.patch').exists()


def test_space_controller_handles_racing_process_exit():
    controller = (ROOT / 'scripts/sugar-gtk4-space.sh').read_text()
    # pgrep can observe a helper that exits before /proc is read. The guard
    # keeps set -e from aborting a valid Space switch in that race.
    assert controller.count('[ -r "/proc/$pid/environ" ] || continue') >= 3
