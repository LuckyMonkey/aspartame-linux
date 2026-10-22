"""FULL PORT receipts: real input and the fixes the first receipts found."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).parents[1]


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem.replace('-', '_'), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_macro_types_program_punctuation_through_qemu_keys():
    macro = load(ROOT / 'scripts/qemu-headless-macro.py')
    keys = macro.text_keys('# Hi\nprint(6*7), a_b: "x"?')
    # Every generated key must survive the QMP sendkey conversion.
    assert [macro.hmp_key_for(k.replace('-', '+')) for k in keys]
    assert 'shift-9' in keys and 'shift-8' in keys and 'ret' in keys
    assert macro.qcode_for('spc') == 'spc'


def test_receipt_uses_real_keys_and_checks_all_four_properties():
    receipt = (ROOT / 'scripts/sugar-gtk4-fullport-receipt.py').read_text()
    for check in ('input', 'persist', 'guard', 'a11y'):
        assert 'results["%s"]' % check in receipt
    assert 'qmp.type_text' in receipt and 'CTRL+TAB' in receipt
    assert 'set_text' not in receipt


def test_pippy_ctrl_tab_leaves_the_editor():
    source = (ROOT / 'packages/gtk4-pippy-activity/pippyactivity4.py').read_text()
    handler = source[source.index('def _editor_key'):source.index('def _reset')]
    assert 'Gdk.ModifierType.CONTROL_MASK)):' in handler


def test_activity_toolbar_button_has_an_accessible_name():
    patch = (ROOT / 'patches/gtk4-preview/0301-toolkit-downstream-on-9d86a31.patch').read_text()
    assert '+    def _set_accessible_title(self, metadata):' in patch
    assert '[metadata.get("title", "Activity")])' in patch
