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


def test_activity_service_exposes_the_shell_lifecycle_boundary():
    patch = _patch("0023-toolkit-activity-dbus-lifecycle.patch")

    assert "class ActivityService(dbus.service.Object):" in patch
    assert '"org.laptop.Activity" + activity_id' in patch
    assert '"/org/laptop/Activity/" + activity_id' in patch
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
    ):
        assert patch_name in build

    assert 'test -x "$venv/bin/sugar-activity4"' in build
    assert 'test -x "$venv/bin/sugar-activity4"' in run
    assert 'test -f "$prefix/share/sugar/activities/Log.activity/activity/activity.info"' in run


def test_unsupported_activity_reports_launch_failure_instead_of_pulsing():
    patch = _patch("0022-toolkit-activity-launch.patch")

    assert "except (RuntimeError, ValueError) as error:" in patch
    assert 'logging.error("GTK4 Activity %s cannot launch: %s",' in patch
    assert "_notify_launch_failed(handle.activity_id)" in patch
    assert "return None" in patch
    assert 'launcher_name == "sugar-activity3"' in patch
    assert "GTK3 bundle cannot run inside isolated GTK4 Activity compositor" in patch
