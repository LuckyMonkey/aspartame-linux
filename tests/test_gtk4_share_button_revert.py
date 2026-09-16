"""The Share palette must not leave the toolbar claiming a share.

Activity.share() raises NotImplementedError in the GTK4 port. Unhandled,
the exception is swallowed by GTK and the radio stays on "My
Neighborhood", so the activity reports itself as shared when nothing was
shared at all.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / ('patches/gtk4-preview/'
                '0149-share-button-reverts-when-sharing-unavailable.patch')


def _added():
    return '\n'.join(line[1:] for line in PATCH.read_text().splitlines()
                     if line.startswith('+') and not line.startswith('+++'))


def test_patch_catches_the_refusal():
    assert 'except NotImplementedError' in _added()


def test_patch_defers_the_revert():
    # RadioPalette's own clicked handler runs after this one and would
    # re-activate the button, so the undo has to outlive the emission.
    added = _added()
    assert 'GLib.idle_add(self._revert_to_private)' in added
    assert 'from gi.repository import GLib' in added


def test_patch_reverts_through_the_same_path_the_user_takes():
    # Clicking Private drives the palette too, so the menu button's icon
    # and label follow the radio back.
    assert 'self.private.emit("clicked")' in _added()


def test_patch_tells_the_user():
    added = _added()
    assert 'NotifyAlert()' in added
    assert 'Sharing is unavailable' in added


def test_patch_does_not_implement_sharing():
    # The fix is about the lie, not the feature.
    body = PATCH.read_text()
    assert 'def share' not in body
    assert 'presenceservice' not in body


def test_build_routes_the_patch_to_the_toolkit():
    build = (ROOT / 'scripts/sugar-gtk4-build.sh').read_text()
    assert '*0149*) target="$toolkit" ;;' in build
