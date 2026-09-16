"""Journal main view must not skip its canvas assignment.

show_main_view() is the only place that installs the Journal's main view as
the canvas. A bare '_active_view == MAIN' early return bypasses that, and
because _active_view starts as MAIN the Journal is then blank forever.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / 'patches/gtk4-preview/0144-journal-main-view-needs-canvas.patch'


def _patch_text():
    return PATCH.read_text()


def test_patch_removes_every_bare_main_view_guard():
    removed = [line for line in _patch_text().splitlines()
               if line.startswith('-') and '_active_view == JournalViews.MAIN' in line]
    # Six bare guards, each a two-line 'if'/'return' pair.
    assert len(removed) >= 6, removed


def test_patch_keeps_the_compound_guard_that_checks_the_canvas():
    lines = _patch_text().splitlines()
    # The canvas-aware guard survives as context, and nothing removes it.
    assert any(line.startswith(' ') and 'self.canvas == self._main_view' in line
               for line in lines), 'the canvas-aware guard must survive'
    assert not any(line.startswith('-') and 'self.canvas == self._main_view' in line
                   for line in lines), 'the canvas-aware guard must not be removed'


def test_patch_targets_show_main_view():
    assert 'def show_main_view' in _patch_text()


def test_build_routes_the_patch_to_the_shell_checkout():
    build = (ROOT / 'scripts/sugar-gtk4-build.sh').read_text()
    assert '*0144*) target="$root/sources/sugar" ;;' in build
