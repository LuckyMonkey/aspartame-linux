from pathlib import Path


ROOT = Path(__file__).parents[1]
PATCH = ROOT / "patches/gtk4-preview/0029-log-activity-gtk4-list.patch"
BUILD = ROOT / "scripts/sugar-gtk4-build.sh"


def _added_lines(patch):
    return "\n".join(
        line[1:]
        for line in patch.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    )


def test_log_activity_replaces_removed_gtk3_tree_widgets():
    patch = PATCH.read_text()
    added = _added_lines(patch)

    assert "Gtk.ListBox()" in added
    assert "Gtk.ListBoxRow()" in added
    assert "Gtk.TreeView" not in added
    assert "Gtk.TreeStore" not in added
    assert "Gtk.CellRendererText" not in added
    assert "monitor_file(" in added
    assert "def _row_selected_cb" in added
    assert "if not self.search_text:" in added


def test_log_activity_patch_is_applied_to_the_pinned_bundle():
    build = BUILD.read_text()

    assert '*0029*) target="$log_activity" ;;' in build
    assert 'test -d "$log_activity/.git"' in build
    assert 'test -f "$log_activity/logviewer.py"' in build
    assert 'log_activity="$root/sources/log-activity"' in build
    assert build.index('log_activity="$root/sources/log-activity"') < build.index(
        'for patch in "$patch_dir"/*.patch'
    )


def test_build_has_bounded_compatibility_for_pinned_log_patch():
    build = BUILD.read_text()

    assert "patch --dry-run --fuzz=5" in build
    assert "applied compatibility preview patch" in build
    assert "def _get_shell_interface" in build
    assert "class ActivityService" in build
