"""Home's Favorites ring must be reachable and operable from the keyboard.

Two GTK3 assumptions broke it: can-focus changed meaning in GTK4 and now gates
a widget's whole subtree, and CanvasIcon only emitted "activate" from a click
even though it advertises AccessibleRole.BUTTON.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAVOURITES = ROOT / 'patches/gtk4-preview/0146-home-focus-enters-favorites-ring.patch'
ICON = ROOT / 'patches/gtk4-preview/0147-icon-keyboard-activation.patch'


def _added(patch):
    return '\n'.join(line[1:] for line in patch.read_text().splitlines()
                     if line.startswith('+') and not line.startswith('+++'))


def _removed(patch):
    return '\n'.join(line[1:] for line in patch.read_text().splitlines()
                     if line.startswith('-') and not line.startswith('---'))


def test_favorites_container_no_longer_gates_its_children():
    assert 'set_can_focus(False)' in _removed(FAVOURITES)
    assert 'set_focusable(False)' in _added(FAVOURITES)


def test_favorites_container_is_still_not_a_focus_stop():
    # The container must not start swallowing focus itself.
    assert 'set_focusable(True)' not in _added(FAVOURITES)


def test_icon_activates_on_enter_and_space():
    added = _added(ICON)
    for key in ('Gdk.KEY_Return', 'Gdk.KEY_KP_Enter', 'Gdk.KEY_space'):
        assert key in added, key
    assert 'self.emit("activate")' in added


def test_icon_reuses_the_existing_signals():
    # No new activation path: the same signals the click gesture emits.
    added = _added(ICON)
    assert 'self.emit("clicked")' in added
    assert 'GObject.Signal' not in added


def test_build_routes_both_patches():
    build = (ROOT / 'scripts/sugar-gtk4-build.sh').read_text()
    assert '*0146*) target="$root/sources/sugar" ;;' in build
    assert '*0147*) target="$toolkit" ;;' in build
