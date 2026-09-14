from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_desktop_overlay_extends_jarabe_package_path():
    init = ROOT / "gtk4-overlay/src/jarabe/desktop/__init__.py"
    source = init.read_text()
    assert "extend_path" in source
    assert "__path__ = extend_path" in source


def test_home_list_help_metadata_does_not_import_gtk3_view_modules():
    source = (ROOT / "gtk4-overlay/src/jarabe/desktop/activitieslist.py").read_text()
    assert "def register_target(widget, target_id, **metadata):" in source
    assert "jarabe.view.contexthelp" not in source


def test_gtk4_runner_excludes_gtk3_overlay_path():
    runner = (ROOT / "scripts/sugar-gtk4-run.sh").read_text()
    assert 'PYTHONPATH="$project_root/gtk4-overlay/src:$datastore_site' in runner
    assert 'PYTHONPATH="$project_root/gtk4-overlay/src:$project_root/sugar-overlay' not in runner
