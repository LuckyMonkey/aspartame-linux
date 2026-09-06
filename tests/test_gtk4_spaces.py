from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_spaces_controller_uses_existing_metacity_workspaces():
    controller = (ROOT / 'scripts/sugar-gtk4-space.sh').read_text()
    assert 'switch-to-workspace-1' in controller
    assert 'switch-to-workspace-2' in controller
    assert 'F7' in controller
    assert 'F8' in controller
    assert 'sugar-gtk4-run.sh' in controller
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
    assert 'did not retain the F7/F8' in controller
    assert 'wmctrl' not in controller
    assert 'xdotool' not in controller


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
