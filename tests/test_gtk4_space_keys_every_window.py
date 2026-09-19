"""F7/F8 must reach the shell from every window it owns.

Sugar disables all window manager keybindings at startup, so the Metacity
`switch-to-workspace-1 = ['F7']` binding can never fire and the Space keys
have to be shell actions. They were bolted onto the main window only, and
the control panel is a plain Gtk.Window that never joins the application,
so nothing listened for F7 while Settings was open.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / ('patches/gtk4-preview/'
                '0153-shell-space-keys-work-from-every-window.patch')


def _added():
    return '\n'.join(line[1:] for line in PATCH.read_text().splitlines()
                     if line.startswith('+') and not line.startswith('+++'))


def _removed():
    return '\n'.join(line[1:] for line in PATCH.read_text().splitlines()
                     if line.startswith('-') and not line.startswith('---'))


def test_space_keys_become_shell_actions():
    added = _added()
    assert "'F7': 'space_classic'," in added
    assert "'F8': 'space_modern'," in added
    assert 'def handle_space_classic' in added
    assert 'def handle_space_modern' in added


def test_the_switcher_stays_overridable():
    # The classic overlay honours the same variable; keep them in step.
    assert "ASPARTAME_SPACE_SWITCHER" in _added()


def test_main_window_no_longer_owns_the_space_keys():
    # 0153 took F7/F8 out of main.py; the consolidated main.py patch is the
    # end state, so assert the absence there rather than a removal line.
    main = (ROOT / 'patches/gtk4-preview/'
            '0157-main-shell-window-consolidated.patch').read_text()
    assert 'space_keys = {Gdk.KEY_F7: "gtk3", Gdk.KEY_F8: "gtk4"}' not in main
    assert '_capture_space_key' not in main
    assert 'Gdk.KEY_F7' not in main


def test_zoom_keys_keep_their_own_handling():
    # Only the Space half moves; F1-F6 stay where they were.
    removed = _removed()
    assert '_capture_zoom_key' not in removed.replace(
        '_surface_controller.connect("key-pressed", _capture_space_key)', '')


def test_control_panel_registers_with_the_key_handler():
    added = _added()
    assert 'from jarabe.view import keyhandler as _keyhandler' in added
    assert '_handler.add_window(self)' in added


def test_control_panel_does_not_join_the_application():
    # ShellModel._window_added_cb would turn it into a phantom activity.
    added = _added()
    assert 'application=' not in added
    assert 'add_window(self)' in added


def test_subprocess_is_imported_where_it_is_now_used():
    assert 'import subprocess' in _added()


def test_build_routes_the_patch_to_the_shell_checkout():
    build = (ROOT / 'scripts/sugar-gtk4-build.sh').read_text()
    assert '*0153*) target="$root/sources/sugar" ;;' in build


def test_build_verifies_semantic_result_after_patch_drift():
    build = (ROOT / 'scripts/sugar-gtk4-build.sh').read_text()
    assert 'verified existing Space key ownership from every shell window' in build
    assert 'grep -q "def handle_space_classic"' in build
