from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "patches/gtk4-preview/0180-toolkit-activity-sharing.patch"
BUILD = ROOT / "scripts/sugar-gtk4-build.sh"


def test_gtk4_activity_uses_the_existing_presence_service():
    patch = PATCH.read_text()

    assert "from sugar4.presence import presenceservice" in patch
    assert "presenceservice.get_instance().get_activity" in patch
    assert "self.shared_activity.join()" in patch
    assert 'self._set_up_sharing(mesh_instance, share_scope)' in patch


def test_gtk4_activity_share_and_invite_follow_the_sugar_contract():
    patch = PATCH.read_text()

    assert 'pservice.connect("activity-shared", self.__share_cb)' in patch
    assert 'pservice.share_activity(self, private=private)' in patch
    assert 'pservice.get_buddy(account_path, contact_id)' in patch
    assert 'self.shared_activity.invite(' in patch
    assert "No active presence connection is available" in patch


def test_share_integration_is_routed_to_the_toolkit_with_bounded_fallback():
    build = BUILD.read_text()

    assert '*0180*) target="$toolkit" ;;' in build
    assert '"$patch_name" == *0180*' in build
    assert 'applied GTK4 Activity sharing integration' in build
    assert 'patch --dry-run --fuzz=5 -p1' in build
