"""Alt+Shift global keys must match the table's lowercase names.

Holding Shift makes the keyval the capital letter, so keyval_name()
returns 'M'. The branch that builds '<alt><shift>m' tested membership in
a lowercase list, never fired, and every Alt+Shift global key was dead.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / ('patches/gtk4-preview/'
                '0152-keyhandler-alt-shift-letters-are-uppercase.patch')


def _lines(prefix):
    return [line[1:] for line in PATCH.read_text().splitlines()
            if line.startswith(prefix)
            and not line.startswith(prefix * 3)]


def test_patch_tests_the_lowercase_form():
    added = '\n'.join(_lines('+'))
    assert "key.lower() in ['f', 'm', 'o', 'q', 'd']" in added


def test_patch_builds_the_key_from_the_lowercase_form():
    added = '\n'.join(_lines('+'))
    assert "key = '<alt><shift>' + key.lower()" in added


def test_patch_removes_the_case_sensitive_comparison():
    removed = '\n'.join(_lines('-'))
    assert "key in ['f', 'm', 'o', 'q', 'd']" in removed
    assert "key = '<alt><shift>' + key" in removed


def test_patch_leaves_the_other_alt_branches_alone():
    removed = '\n'.join(_lines('-'))
    assert 'Tab' not in removed
    assert 'Escape' not in removed
    assert 'F11' not in removed


def test_patch_still_gates_on_shift():
    # Alt+m without Shift must not become the Alt+Shift action, so the
    # SHIFT_MASK test has to survive as context rather than be removed.
    assert 'state & Gdk.ModifierType.SHIFT_MASK' not in '\n'.join(_lines('-'))
    assert ' ' + 'if state & Gdk.ModifierType.SHIFT_MASK:' in PATCH.read_text()


def test_build_routes_the_patch_to_the_shell_checkout():
    build = (ROOT / 'scripts/sugar-gtk4-build.sh').read_text()
    assert '*0152*) target="$root/sources/sugar" ;;' in build
