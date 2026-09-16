"""Sugar tool button accelerators must survive the launch ordering.

activityinstance constructs the Activity, toolbar and all, and only then
calls app.add_window(). A ToolButton's notify::root therefore fires while
root.get_application() is still None, so the Gio action is never created.
ToggleToolButton already retries on map; ToolButton did not.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / 'patches/gtk4-preview/0150-toolbutton-accelerator-installed-on-map.patch'


def _added():
    return '\n'.join(line[1:] for line in PATCH.read_text().splitlines()
                     if line.startswith('+') and not line.startswith('+++'))


def test_patch_retries_on_map():
    added = _added()
    assert 'tool_button.connect("map"' in added
    assert '_add_accelerator(tool_button)' in added


def test_patch_keeps_the_root_notification():
    # The map retry is an addition, not a replacement.
    removed = [line for line in PATCH.read_text().splitlines()
               if line.startswith('-') and 'notify::root' in line]
    assert not removed


def test_patch_replaces_rather_than_leaks_the_action():
    # map fires again after an unmap, so a second install must not stack
    # another action on the application.
    added = _added()
    assert 'app.remove_action(previous)' in added
    assert 'tool_button._accel_action_name = action_name' in added


def test_patch_touches_only_the_tool_button():
    body = PATCH.read_text()
    assert 'toggletoolbutton.py' not in body, 'the sibling already works'


def test_build_routes_the_patch_to_the_toolkit():
    build = (ROOT / 'scripts/sugar-gtk4-build.sh').read_text()
    assert '*0150*) target="$toolkit" ;;' in build


def test_key_probe_can_send_a_control_chord():
    # The runtime proof needs Ctrl+Q from the QEMU keyboard.
    probe = (ROOT / 'scripts/qemu-send-key.py').read_text()
    assert 'CTRL+{name}' in probe
