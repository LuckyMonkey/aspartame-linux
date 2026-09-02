import importlib.util
import sys
from pathlib import Path

MODULE = Path(__file__).parents[1] / "archiso/aspartame/airootfs/usr/share/aspartame/aspartame_help.py"
spec = importlib.util.spec_from_file_location("aspartame_help", MODULE)
help_module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = help_module
spec.loader.exec_module(help_module)


def test_initial_targets_have_plain_language_metadata():
    targets = {item.id: item for item in help_module.all_targets()}
    expected = {
        "org.aspartame.shell.help",
        "org.aspartame.shell.home",
        "org.aspartame.shell.journal",
        "org.aspartame.shell.neighborhood",
        "org.aspartame.count.total",
        "org.aspartame.count.layer.copy",
    }
    assert expected <= targets.keys()
    assert all(item.title and item.explanation for item in targets.values())


def test_mode_marker_can_be_toggled(tmp_path):
    original = help_module.MODE_FILE
    help_module.MODE_FILE = tmp_path / "mode"
    try:
        help_module.set_active(False)
        assert not help_module.is_active()
        assert help_module.toggle()
        assert help_module.is_active()
        assert not help_module.toggle()
        assert not help_module.is_active()
    finally:
        help_module.MODE_FILE = original


class FakeAccessible:
    def __init__(self):
        self.name = None
        self.description = None

    def set_name(self, value):
        self.name = value

    def set_description(self, value):
        self.description = value


class FakeWidget:
    def __init__(self):
        self.accessible = FakeAccessible()
        self.focus = None

    def set_can_focus(self, value):
        self.focus = value

    def get_accessible(self):
        return self.accessible


def test_register_target_sets_keyboard_accessible_metadata():
    widget = FakeWidget()
    target = help_module.register_target(
        widget, "org.aspartame.test.accessible",
        title="Example", short_description="Explain the example.",
        explanation="This explains the example.")
    assert target.title == "Example"
    assert widget.focus is True
    assert widget.accessible.name == "Example"
    assert widget.accessible.description == "Explain the example."
