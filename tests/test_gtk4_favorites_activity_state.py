from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_favorites_ring_uses_authoritative_activity_presentation():
    patch = (ROOT / 'patches/gtk4-preview/'
             '0168-home-favorites-authoritative-activity-state.patch').read_text()
    assert 'activitypresentation.get_model()' in patch
    assert "state in ('launching', 'running', 'active')" in patch
    assert 'A stopped Activity is still resumable' in patch


def test_build_routes_and_verifies_favorites_state_patch():
    build = (ROOT / 'scripts/sugar-gtk4-build.sh').read_text()
    assert '*0168*) target="$root/sources/sugar" ;;' in build
    assert 'verified authoritative Favorites Activity state' in build
