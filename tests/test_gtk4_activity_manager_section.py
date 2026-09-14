from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_gtk4_activity_manager_is_native_and_registry_backed():
    view = (ROOT / "gtk4-overlay/src/cpsection/activities/view.py").read_text()
    model = (ROOT / "gtk4-overlay/src/cpsection/activities/model.py").read_text()
    patch = (ROOT / "patches/gtk4-preview/0112-controlpanel-activity-manager-section.patch").read_text()
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert "class ActivityManager(SectionView)" in view
    assert "System-managed" in view
    assert "_remove_clicked" in view
    assert "bundleregistry.get_registry()" in model
    assert "aspartame-sudo-askpass" in model
    assert "shutil.move(path, target)" in model
    assert "import cpsection.activities" in patch
    assert '*0112*) target="$root/sources/sugar" ;;' in build
