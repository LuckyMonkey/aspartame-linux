"""Sugar tool buttons must carry an accessible name.

The palette replaces the GTK tooltip, so clearing the native tooltip is
correct, but it left icon-only buttons anonymous to assistive technology.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / 'patches/gtk4-preview/0148-toolbutton-accessible-name-from-tooltip.patch'


def _added():
    return '\n'.join(line[1:] for line in PATCH.read_text().splitlines()
                     if line.startswith('+') and not line.startswith('+++'))


def test_patch_sets_the_accessible_label():
    added = _added()
    assert 'Gtk.AccessibleProperty.LABEL' in added
    assert 'update_property' in added


def test_patch_uses_the_same_text_as_the_palette():
    # The name must come from the tooltip argument, not a new string.
    assert '[tooltip]' in _added()


def test_patch_keeps_the_native_tooltip_cleared():
    # Clearing the GTK tooltip is deliberate; the fix must not undo it.
    removed = [line for line in PATCH.read_text().splitlines()
               if line.startswith('-') and 'set_tooltip_text' in line]
    assert not removed


def test_build_routes_the_patch_to_the_toolkit():
    build = (ROOT / 'scripts/sugar-gtk4-build.sh').read_text()
    assert '*0148*) target="$toolkit" ;;' in build
