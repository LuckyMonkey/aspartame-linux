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
