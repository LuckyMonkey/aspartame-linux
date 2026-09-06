from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_activity_review_capture_passes_the_screenshot_variable():
    capture = (ROOT / "scripts/activity-review-capture.sh").read_text()
    screenshot = (ROOT / "scripts/sugar-screenshot.sh").read_text()

    assert 'SCREENSHOT_DIR="$out"' in capture
    assert 'SUGAR_SCREENSHOT_DIR=' not in capture
    assert "output_dir=${SCREENSHOT_DIR:-" in screenshot


def test_sugar_reload_can_write_every_shared_visual_asset():
    reload_script = (ROOT / "scripts/sugar-reload.sh").read_text()

    assert 'sudo install -D -m 0644 "$project_root/archiso/aspartame/airootfs/usr/share/aspartame/aspartame_visual.py"' in reload_script


def test_make_test_runs_the_python_suite_after_static_smoke_checks():
    makefile = (ROOT / "Makefile").read_text()

    assert "test:\n\t./scripts/smoke-test.sh\n\tpython3 -m pytest -q tests\n" in makefile


def test_gtk4_tools_share_the_same_guest_preview_default():
    expected = "/home/aspartame/Development/gtk4-preview"
    for name in (
        "sugar-gtk4-smoke.sh",
        "sugar-gtk4-check.sh",
        "sugar-gtk4-update.sh",
        "sugar-gtk4-upstream-status.sh",
    ):
        source = (ROOT / "scripts" / name).read_text()
        assert f"GTK4_ROOT:-{expected}" in source, name


def test_management_enrollment_fails_closed_without_a_configured_secret():
    server = (ROOT / "management/server.py").read_text()

    assert 'os.environ.get("ASPARTAME_ENROLLMENT_TOKEN")' in server
    assert '"enrollment disabled; set ASPARTAME_ENROLLMENT_TOKEN"' in server
    assert 'os.environ.get("ASPARTAME_ENROLLMENT_TOKEN", "change-me-before-enrollment")' not in server
