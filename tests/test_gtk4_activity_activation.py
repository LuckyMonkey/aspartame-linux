from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_single_process_activity_activation_reuses_window():
    patch = (ROOT / "patches/gtk4-preview/0047-toolkit-single-process-activation-guard.patch").read_text()
    assert "_sugar_activity_instance" in patch
    assert "re-presenting existing Activity" in patch
    assert "app.add_window(activity)" in patch


def test_activity_activation_guard_is_routed_by_guest_build():
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert "*0047*) target=\"$root/sources/sugar\"" in build
    assert '"$patch_name" == *0047*' in build
