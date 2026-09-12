from pathlib import Path


ROOT = Path(__file__).parents[1]
PATCH_DIR = ROOT / "patches/gtk4-preview"


def _patch(name):
    return (PATCH_DIR / name).read_text()


def test_activity_launch_patch_owns_the_child_process_contract():
    patch = _patch("0022-toolkit-activity-launch.patch")

    assert "def create(bundle, handle):" in patch
    assert "subprocess.Popen(" in patch
    assert "pass_fds=(client_fd,)" in patch
    assert 'environment["GDK_BACKEND"] = "wayland"' in patch
    assert 'environment["WAYLAND_SOCKET"] = str(client_fd)' in patch
    assert "GLib.child_watch_add(" in patch
    assert "os.close(client_fd)" in patch
    assert "_notify_launch_failed(handle.activity_id)" in patch
    id_patch = _patch("0035-toolkit-activity-id-argument.patch")
    assert 'command.extend(["--activity-id", handle.activity_id])' in id_patch


def test_activity_service_exposes_the_shell_lifecycle_boundary():
    patch = _patch("0023-toolkit-activity-dbus-lifecycle.patch")
    path_patch = _patch("0033-toolkit-activity-object-path.patch")

    assert "class ActivityService(dbus.service.Object):" in patch
    assert '"org.laptop.Activity" + activity_id' in patch
    assert 'object_id = activity_id.replace("-", "_")' in path_patch
    assert '"/org/laptop/Activity/" + object_id' in path_patch
    assert "def SetActive(self, active):" in patch
    assert "def Close(self):" in patch
    assert "def close(self):" in patch
    assert "self.remove_from_connection()" in patch


def test_activity_entrypoint_and_window_cleanup_are_wired():
    entrypoint = (ROOT / "scripts/sugar-activity4").read_text()
    lifecycle = _patch("0025-toolkit-activity-lifecycle.patch")

    assert "sugar4.activity.activityinstance" in entrypoint
    assert "from sugar4.activity.activityservice import ActivityService" in lifecycle
    assert "self._activity_service = ActivityService(self)" in lifecycle
    assert "self._activity_service.close()" in lifecycle
    assert "application.remove_window(self)" in lifecycle
    assert "application.quit()" in lifecycle


def test_build_routes_and_runtime_requires_the_lifecycle_surface():
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    run = (ROOT / "scripts/sugar-gtk4-run.sh").read_text()

    for patch_name in (
        "*0022*",
        "*0023*",
        "*0024*",
        "*0025*",
        "*0030*",
        "*0033*",
        "*0034*",
        "*0035*",
        "*0036*",
    ):
        assert patch_name in build

    assert 'test -x "$venv/bin/sugar-activity4"' in build
    assert 'test -x "$venv/bin/sugar-activity4"' in run
    assert 'test -f "$prefix/share/sugar/activities/Log.activity/activity/activity.info"' in run


def test_activity_object_path_encoding_is_routed_to_toolkit_and_shell():
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    shell_patch = _patch("0034-shell-activity-object-path.patch")
    assert "*0033*" in build
    assert "*0034*" in build
    assert "def _get_service_path(self):" in shell_patch
    assert "replace('-', '_')" in shell_patch


def test_shell_registers_casilda_activity_before_spawn():
    patch = _patch("0036-shell-notify-activity-launch.patch")
    assert "shell_model.notify_launch(activity_id, bundle.get_bundle_id())" in patch


def test_unsupported_activity_reports_launch_failure_instead_of_pulsing():
    patch = _patch("0022-toolkit-activity-launch.patch")

    assert "except (RuntimeError, ValueError) as error:" in patch
    assert 'logging.error("GTK4 Activity %s cannot launch: %s",' in patch
    assert "_notify_launch_failed(handle.activity_id)" in patch
    assert "return None" in patch
    assert 'launcher_name == "sugar-activity3"' in patch
    assert "GTK3 bundle cannot run inside isolated GTK4 Activity compositor" in patch


def test_current_toolkit_pin_receives_the_gtk3_launcher_guard():
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    patch = _patch("0030-toolkit-reject-gtk3-launchers.patch")
    assert "*0030*" in build
    assert 'launcher_name == "sugar-activity3"' in patch
