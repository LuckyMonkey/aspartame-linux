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
