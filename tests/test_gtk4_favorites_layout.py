from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_favorites_layout_handles_unkeyed_peer_icons_without_crashing():
    patch = (ROOT / 'patches/gtk4-preview/0172-favorites-layout-none-positioning-data.patch').read_text()
    assert 'if positioning_data is None:' in patch
    assert 'type(child).__qualname__' in patch
    assert 'id(child)' in patch
    assert 'positioning_data.encode' in patch


def test_neighborhood_empty_state_tracks_peer_and_activity_content():
    patch = (ROOT / 'patches/gtk4-preview/'
             '0174-mesh-empty-state-follows-peer-content.patch').read_text()
    build = (ROOT / 'scripts/sugar-gtk4-build.sh').read_text()
    assert 'def _update_empty_state(self):' in patch
    assert 'has_content = bool(self._buddies or self._activities)' in patch
    assert 'self._empty_state.set_visible(not has_content)' in patch
    assert 'self._update_empty_state()' in patch
    assert '*0174*) target="$root/sources/sugar" ;;' in build


def test_favorites_accessibility_and_lifecycle_order_are_repaired():
    patch = (ROOT / 'patches/gtk4-preview/'
             '0175-favorites-accessibility-and-lifecycle-order.patch').read_text()
    build = (ROOT / 'scripts/sugar-gtk4-build.sh').read_text()
    assert 'self.set_focusable(True)' in patch
    assert '[activity_info.get_name()]' in patch
    assert 'self._presentation = activitypresentation.get_model()' in patch
    assert 'self._refresh()' in patch
    assert '*0175*) target="$root/sources/sugar" ;;' in build
