from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_show_list_action_targets_native_home_list():
    patch = (ROOT / "patches/gtk4-preview/0101-shell-show-list-action.patch").read_text()
    assert "def show_list_view(self)" in patch
    assert "def ShowList(self)" in patch
    assert "get_home_box().show_list_view()" in patch


def test_show_list_patch_is_routed_and_idempotent():
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert '*0101*) target="$root/sources/sugar" ;;' in build
    assert "verified existing ShowList action" in build


def test_navigation_dismisses_modal_control_panel():
    patch = (ROOT / "patches/gtk4-preview/0102-shell-navigation-closes-control-panel.patch").read_text()
    assert "def _close_control_panel(self)" in patch
    assert "self._close_control_panel()" in patch


def test_duplicate_navigation_methods_are_covered():
    patch = (ROOT / "patches/gtk4-preview/0103-shell-navigation-modal-duplicates.patch").read_text()
    assert "ShowNeighborhood" in patch
    assert "ShowGroup" in patch
    assert "ShowHome" in patch
    assert "ShowList" in patch
    assert patch.count("self._shell_model._set_active_activity(None)") == 4


def test_journal_canvas_reattach_is_deferred_when_still_rooted():
    patch = (ROOT / "patches/gtk4-preview/0104-journal-defer-rooted-canvas.patch").read_text()
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert "widget.get_root() is not None" in patch
    assert "GLib.idle_add(self.set_canvas, widget)" in patch
    assert '*0104*) target="$root/sources/sugar" ;;' in build


def test_journal_main_view_restoration_is_idempotent():
    patch = (ROOT / "patches/gtk4-preview/0144-journal-main-view-needs-canvas.patch").read_text()
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert "self._active_view == JournalViews.MAIN" in patch
    assert "self._active_view == JournalViews.MAIN and" in patch
    assert "self.canvas == self._main_view" in patch
    assert patch.count("+            return") == 1
    assert '*0144*) target="$root/sources/sugar" ;;' in build


def test_journal_detail_escape_returns_to_main_view():
    patch = (ROOT / "patches/gtk4-preview/0107-journal-escape-detail-back.patch").read_text()
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert "if keyname == 'Escape':" in patch
    assert "self.show_main_view()" in patch
    assert '*0107*) target="$root/sources/sugar" ;;' in build


def test_keyhandler_routes_escape_for_journal_detail():
    patch = (ROOT / "patches/gtk4-preview/0108-keyhandler-journal-detail-escape.patch").read_text()
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert "active_activity.show_main_view()" in patch
    assert "hasattr(active_activity" in patch
    assert '*0108*) target="$root/sources/sugar" ;;' in build


def test_obsolete_journal_patches_are_retired():
    assert not (ROOT / "patches/gtk4-preview/0106-journal-main-view-idempotent.patch").exists()
    assert not (ROOT / "patches/gtk4-preview/0109-journal-defer-rooted-toolbar.patch").exists()
