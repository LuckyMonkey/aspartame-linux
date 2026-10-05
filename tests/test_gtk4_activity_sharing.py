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


def test_share_control_has_a_visible_icon_and_accessible_name():
    patch = (ROOT /
             "patches/gtk4-preview/0181-toolkit-share-button-visible.patch").read_text()

    assert 'kwargs.setdefault("icon_name", "zoom-neighborhood")' in patch
    assert 'kwargs.setdefault("tooltip", _("Share"))' in patch
    assert 'self.set_tooltip(_("Share"))' in patch


def test_share_palette_options_have_actionable_accessible_names():
    patch = (ROOT /
             "patches/gtk4-preview/0182-radiopalette-option-accessibility.patch").read_text()

    assert "Gtk.AccessibleProperty.LABEL" in patch
    assert "[label]" in patch


def test_share_integration_is_routed_to_the_toolkit_with_bounded_fallback():
    build = BUILD.read_text()

    assert '*0180*) target="$toolkit" ;;' in build
    assert '"$patch_name" == *0180*' in build
    assert 'applied GTK4 Activity sharing integration' in build
    assert 'patch --dry-run --fuzz=5 -p1' in build
    assert '*0181*) target="$toolkit" ;;' in build
    assert '"$patch_name" == *0181*' in build
    assert '*0182*) target="$toolkit" ;;' in build
    assert '"$patch_name" == *0182*' in build


def test_friends_tray_ignores_activity_announcements_without_active_app():
    patch = (ROOT /
             "patches/gtk4-preview/0183-friends-tray-activity-guard.patch").read_text()
    build = BUILD.read_text()

    assert "active_activity is None or shared_activity is None" in patch
    assert '*0183*) target="$root/sources/sugar" ;;' in build
    assert '"$patch_name" == *0183*' in build
    assert "applied GTK4 Friends tray activity guard" in build


def test_neighborhood_removal_signals_are_idempotent():
    patch = (ROOT /
             "patches/gtk4-preview/0184-meshbox-removal-races.patch").read_text()
    build = BUILD.read_text()

    assert "self._buddies.pop(key, None)" in patch
    assert "self._activities.pop(activity_id, None)" in patch
    assert '*0184*) target="$root/sources/sugar" ;;' in build
    assert '"$patch_name" == *0184*' in build
    assert "applied GTK4 Neighborhood removal race guard" in build


def test_shell_shared_activity_removal_is_idempotent():
    patch = (ROOT /
             "patches/gtk4-preview/0188-shell-shared-activity-removal-idempotent.patch").read_text()
    build = BUILD.read_text()

    assert "self._shared_activities.pop(activity_id, None)" in patch
    assert '*0188*) target="$root/sources/sugar" ;;' in build


def test_shared_activity_is_published_to_peer_presence():
    patch = (ROOT /
             "patches/gtk4-preview/0185-toolkit-publish-current-activity.patch").read_text()
    build = BUILD.read_text()

    assert "self.telepathy_conn.SetCurrentActivity(" in patch
    assert "self._id," in patch
    assert "self.room_handle," in patch
    assert "CONN_INTERFACE_BUDDY_INFO" in patch
    assert "unable to publish current Activity" in patch
    assert '*0185*) target="$toolkit" ;;' in build
    assert '"$patch_name" == *0185*' in build
    assert "applied GTK4 current Activity presence publication" in build


def test_share_roundtrip_can_qualify_successful_telepathy_mode():
    probe = (ROOT / "scripts/sugar-gtk4-share-roundtrip.py").read_text()

    assert 'ASPARTAME_SHARE_MODE' in probe
    assert '"successful Telepathy share"' in probe
    assert 'Share of activity {activity_id} successful' in probe
    assert 'GetCurrentActivity(' in probe
    assert 'current_activity_published(activity_id)' in probe


def test_share_roundtrip_can_hold_the_owner_for_peer_join():
    probe = (ROOT / "scripts/sugar-gtk4-share-roundtrip.py").read_text()
    assert 'ASPARTAME_SHARE_HOLD_SECONDS' in probe
    assert 'env[option] = os.environ[option]' in probe
    assert 'share_mode == "shared"' in probe


def test_peer_join_probe_uses_the_real_sugar4_presence_join_contract():
    probe = (ROOT / "scripts/sugar-gtk4-share-join-roundtrip.py").read_text()
    assert 'presenceservice.get_instance()' in probe
    assert 'pservice.get_activity(activity_id, warn_if_none=False)' in probe
    assert 'activity.join()' in probe
    assert 'contract=sugar4.presence.Activity' in probe


def test_peer_join_probe_reports_discovery_state_and_failure_phase():
    probe = (ROOT / "scripts/sugar-gtk4-share-join-roundtrip.py").read_text()

    assert 'ASPARTAME_PEER_DEBUG' in probe
    assert 'peer-debug members=' in probe
    assert 'peer-debug candidate activity_id=' in probe
    assert 'peer-debug join-command' in probe
    assert 'peer-debug join-members' in probe
    assert 'phase=discovery' in probe
    assert 'phase=activity-object' in probe
    assert 'phase=join' in probe


def test_peer_observer_uses_the_live_neighborhood_model():
    observer = (ROOT / "scripts/sugar-gtk4-share-peer-observer.py").read_text()

    assert 'buddy_info.GetActivities(' in observer
    assert 'group.GetMembers()' in observer
    assert 'activity_properties.GetProperties(' in observer
    assert 'name != "Calculate Activity"' in observer
    assert 'private' in observer
