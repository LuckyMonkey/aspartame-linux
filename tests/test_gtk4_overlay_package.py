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


def test_home_list_rows_launch_on_primary_pointer_click():
    source = (ROOT / "gtk4-overlay/src/jarabe/desktop/activitieslist.py").read_text()
    assert "Gtk.GestureClick(button=Gdk.BUTTON_PRIMARY)" in source
    assert "Gtk.PropagationPhase.CAPTURE" in source
    assert "def _primary_pressed" in source
    assert "self.owner.run_activity(self.item.bundle_id, True)" in source


def test_home_list_rows_expose_named_button_semantics():
    source = (ROOT / "gtk4-overlay/src/jarabe/desktop/activitieslist.py").read_text()
    assert "self.set_accessible_role(Gtk.AccessibleRole.BUTTON)" in source
    assert "self.set_focusable(True)" in source
    assert "Gtk.AccessibleProperty.LABEL" in source


def test_home_list_rows_activate_with_enter_or_space():
    source = (ROOT / "gtk4-overlay/src/jarabe/desktop/activitieslist.py").read_text()
    assert "Gdk.KEY_Return" in source
    assert "Gdk.KEY_KP_Enter" in source
    assert "Gdk.KEY_space" in source
    assert "self.owner.run_activity(self.item.bundle_id, True)" in source


def test_home_list_uses_existing_gtk4_command_capability_api():
    source = (ROOT / "gtk4-overlay/src/jarabe/desktop/activitieslist.py").read_text()
    assert "def supports_bundle(bundle):" in source
    assert "activityfactory.get_command(bundle)" in source
    assert "activityfactory.supports_bundle" not in source


def test_gtk4_runner_excludes_gtk3_overlay_path():
    runner = (ROOT / "scripts/sugar-gtk4-run.sh").read_text()
    assert 'PYTHONPATH="$project_root/gtk4-overlay/src:$datastore_site' in runner
    assert 'PYTHONPATH="$project_root/gtk4-overlay/src:$project_root/sugar-overlay' not in runner
