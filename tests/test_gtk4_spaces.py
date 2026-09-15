from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_spaces_controller_uses_existing_metacity_workspaces():
    controller = (ROOT / 'scripts/sugar-gtk4-space.sh').read_text()
    assert 'switch-to-workspace-1' in controller
    assert 'switch-to-workspace-2' in controller
    assert 'F7' in controller
    assert 'F8' in controller
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


def test_classic_keyhandler_releases_global_grabs_for_modern_space():
    handler = (ROOT / 'sugar-overlay/src/jarabe/view/keyhandler.py').read_text()
    assert 'SugarExt.KeyGrabber' in handler
    assert 'get_active_workspace' in handler
    assert 'self._key_grabber.grab_keys(keys)' in handler
    assert 'workspace == 0' in handler
    assert 'Spaces key ownership' in handler
    assert 'self._key_grabber = None' in handler
    assert 'SugarExt.KeyGrabber()' in handler
    assert 'for space_key in ("F7", "F8")' in handler
    assert '_actions_table.setdefault("F7"' in handler
    assert '_actions_table.setdefault("F8"' in handler
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
    patch = (ROOT / "patches/gtk4-preview/0027-shell-windowed-frame.patch").read_text()
    assert "Gtk.EventControllerKey()" in patch
    assert "Gtk.PropagationPhase.CAPTURE" in patch
    for key in ("Gdk.KEY_F1", "Gdk.KEY_F2", "Gdk.KEY_F3", "Gdk.KEY_F4"):
        assert key in patch
    assert "shell_instance.set_zoom_level(level)" in patch


def test_gtk4_main_window_routes_space_keys_semantically():
    patch = (ROOT / "patches/gtk4-preview/0061-main-space-key-capture.patch").read_text()
    assert "Gdk.KEY_F7" in patch and "Gdk.KEY_F8" in patch
    assert "ASPARTAME_SPACE_SWITCHER" in patch
    assert "subprocess.Popen" in patch


def test_gtk4_runner_rejects_system_journal_window_import():
    runner = (ROOT / "scripts/sugar-gtk4-run.sh").read_text()
    assert "GTK4 Journal window resolved outside preview sources" in runner
    assert "preview_pythonpath" in runner
    assert "jarabe.journal.journalwindow" in runner


def test_gtk4_global_key_grabber_patch_is_retired_when_sugarext_lacks_api():
    patch = (ROOT / "patches/gtk4-preview/0094-modern-space-keygrabber.patch").read_text()
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert "SugarExt.KeyGrabber" in patch
    assert 'retired unavailable SugarExt global key-grabber preview patch' in build


def test_build_does_not_accept_stale_key_grabber_patch_as_verified():
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert '*0094*) echo "retired unavailable SugarExt global key-grabber preview patch"; continue ;;' in build


def test_invalid_runtime_grabber_block_is_removed_when_present():
    patch = (ROOT / "patches/gtk4-preview/0111-retire-invalid-runtime-grabber-block.patch").read_text()
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert "SugarExt 2.0" in patch
    assert "SugarExt.KeyGrabber" in patch
    assert '*0111*) target="$root/sources/sugar" ;;' in build


def test_mesh_empty_state_and_drift_guards_are_present():
    patch = (ROOT / 'patches/gtk4-preview/0097-mesh-empty-state.patch').read_text()
    build = (ROOT / 'scripts/sugar-gtk4-build.sh').read_text()
    assert 'No people or shared Activities are nearby yet.' in patch
    assert '_empty_state' in patch
    assert 'existing idempotent Activity removal' in build
    assert 'existing Group view gettext import' in build
    assert 'existing Casilda activity key capture' in build
    assert 'existing Frame dismissal on zoom' in build


def test_neighborhood_accessibility_patch_is_routed():
    patch = (ROOT / 'patches/gtk4-preview/0114-neighborhood-accessibility.patch').read_text()
    build = (ROOT / 'scripts/sugar-gtk4-build.sh').read_text()
    assert "AccessibleProperty.LABEL" in patch
    assert "AccessibleRole.GROUP" in patch
    assert '*0114*) target="$root/sources/sugar" ;;' in build
    assert '*0115*) target="$root/sources/sugar" ;;' in build


def test_neighborhood_accessibility_order_fix_is_routed():
    patch = (ROOT / 'patches/gtk4-preview/0127-neighborhood-accessibility-order.patch').read_text()
    build = (ROOT / 'scripts/sugar-gtk4-build.sh').read_text()
    assert 'repair Neighborhood accessibility call ordering' in patch
    assert '*0127*) target="$root/sources/sugar" ;;' in build
    assert 'set_accessible_role(Gtk.AccessibleRole.GROUP)' in patch


def test_zoom_service_dedupe_patch_is_routed():
    patch = (ROOT / 'patches/gtk4-preview/0128-service-dedupe-zoom-actions.patch').read_text()
    build = (ROOT / 'scripts/sugar-gtk4-build.sh').read_text()
    assert 'one authoritative zoom action implementation' in patch
    assert '*0128*) target="$root/sources/sugar" ;;' in build
    assert 'Settings cleanup' in patch


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
    final_patch = (ROOT / 'patches/gtk4-preview/0123-frame-accessibility-relocate-current.patch').read_text()
    build = (ROOT / 'scripts/sugar-gtk4-build.sh').read_text()
    assert "[_('Frame')]" in patch
    assert "AccessibleRole.GROUP" in patch
    assert '*0118*) target="$root/sources/sugar" ;;' in build
    assert '*0119*) target="$root/sources/sugar" ;;' in build
    assert '*0120*) target="$root/sources/sugar" ;;' in build
    assert '*0121*) target="$root/sources/sugar" ;;' in build
    assert '*0122*) target="$root/sources/sugar" ;;' in build
    assert '*0123*) target="$root/sources/sugar" ;;' in build
    assert "Move the accessibility metadata" in final_patch
    assert "self._position = position" in final_patch
    assert "super().do_dispose()" in final_patch
