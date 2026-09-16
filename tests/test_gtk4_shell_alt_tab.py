"""Alt+Tab must walk a list the active activity is actually in.

get_next_activity()/get_previous_activity() indexed
_get_activities_with_window(), which in the modern Space holds only the
shell's own window: an Activity is a Wayland client inside the compositor
and never registers a Gtk window. Every press raised ValueError.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / 'patches/gtk4-preview/0151-shell-alt-tab-walks-tracked-activities.patch'


def _added():
    return '\n'.join(line[1:] for line in PATCH.read_text().splitlines()
                     if line.startswith('+') and not line.startswith('+++'))


def _removed():
    return '\n'.join(line[1:] for line in PATCH.read_text().splitlines()
                     if line.startswith('-') and not line.startswith('---'))


def test_patch_stops_indexing_the_window_filtered_list():
    removed = _removed()
    assert 'activities = self._get_activities_with_window()' in removed
    assert 'i = activities.index(current)' in removed


def test_patch_walks_the_tracked_activities():
    added = _added()
    assert 'def _get_tabbing_activities' in added
    assert 'if activity.get_bundle_id() is not None' in added


def test_patch_guards_the_index():
    # Both the empty list and a current that is not in it.
    added = _added()
    assert added.count('if not activities:') == 2
    assert added.count('if current not in activities:') == 2


def test_patch_checks_emptiness_before_indexing():
    # The original checked len()==0 *after* index(), so it could never run.
    added = _added().splitlines()
    guard = next(i for i, l in enumerate(added) if 'if not activities:' in l)
    index = next(i for i, l in enumerate(added) if 'i = activities.index' in l)
    assert guard < index


def test_patch_leaves_the_window_filter_for_its_other_callers():
    # can_launch_activity_instance() and friends still call it; this fix is
    # only about the two tabbing entry points.
    removed = _removed()
    assert 'def _get_activities_with_window' not in removed
    assert 'ret.append(i)' not in removed


def test_build_routes_the_patch_to_the_shell_checkout():
    build = (ROOT / 'scripts/sugar-gtk4-build.sh').read_text()
    assert '*0151*) target="$root/sources/sugar" ;;' in build
