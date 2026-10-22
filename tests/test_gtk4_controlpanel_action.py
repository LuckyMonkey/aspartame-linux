import ast
from pathlib import Path
import runpy
import subprocess
import sys
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).parents[1]
repair = runpy.run_path(
    str(ROOT / 'scripts/repair-gtk4-controlpanel-action.py'))['repair']
TRUNCATED = '''class UIService:
    def ShowControlPanel(self):
        if self._shell_model.has_modal():
            return False
        from jarabe.controlpanel.gui import ControlPanel
        panel = ControlPanel(0)
        main_window = getattr(self._shell_model, '_main_window', None)
        if main_window is not None:
            panel.set_transient_for(main_window)
        panel.set_visible(True)
'''


def exercise(source, monkeypatch):
    tree = ast.parse(source)
    method = next(node for node in ast.walk(tree)
                  if isinstance(node, ast.FunctionDef)
                  and node.name == 'ShowControlPanel')
    method.decorator_list = []
    namespace = {}
    exec(compile(ast.Module(body=[method], type_ignores=[]), '<action>', 'exec'),
         namespace)
    panel = SimpleNamespace(set_transient_for=lambda parent: None,
                            set_visible=lambda visible: None)
    monkeypatch.setitem(sys.modules, 'jarabe.controlpanel.gui',
                        SimpleNamespace(ControlPanel=lambda window_id: panel))
    model = SimpleNamespace(has_modal=lambda: False, _main_window=object())
    service = SimpleNamespace(_shell_model=model)
    assert namespace['ShowControlPanel'](service) is True
    assert service._control_panel is panel
    model.has_modal = lambda: True
    assert namespace['ShowControlPanel'](service) is False
    assert service._control_panel is panel


def test_repair_retains_window_and_returns_success(monkeypatch):
    result = repair(TRUNCATED)
    exercise(result, monkeypatch)
    assert repair(result) == result


def test_repair_refuses_unknown_implementation():
    with pytest.raises(ValueError, match='unrecognized'):
        repair(TRUNCATED.replace('panel.set_visible(True)', 'panel.present()'))


def test_repair_preserves_upstream_utf8_bom():
    result = repair('\ufeff' + TRUNCATED)
    assert result == '\ufeff' + repair(TRUNCATED)
    assert repair(result) == result


def test_fresh_patch_replays_complete_action(tmp_path, monkeypatch):
    target = tmp_path / 'src/jarabe/view/service.py'
    target.parent.mkdir(parents=True)
    target.write_text('class UIService:\n    def ShowFrame(self):\n'
                      '        from jarabe import frame\n'
                      '        frame.get_view().show()\n        return True\n')
    patch = ROOT / 'patches/gtk4-preview/0058-shell-show-controlpanel-action.patch'
    subprocess.run(['patch', '--batch', '-p1', '-i', str(patch)],
                   cwd=tmp_path, check=True, capture_output=True)
    exercise(target.read_text(), monkeypatch)
    assert repair(target.read_text()) == target.read_text()


def test_build_and_packaging_repair_old_exports():
    for name in ('sugar-gtk4-build.sh', 'build-iso.sh'):
        assert 'scripts/repair-gtk4-controlpanel-action.py' in (
            ROOT / 'scripts' / name).read_text()
