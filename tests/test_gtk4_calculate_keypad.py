"""Calculate's keypad must actually insert into the expression entry.

Gtk.Editable.insert_text takes (text, position). Passing a separate length
raised TypeError inside the clicked handler on every press, so every digit and
operator button silently did nothing while Clear and = kept working.
"""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'packages/gtk4-calculate-activity/calculateactivity4.py'


def _insert_text_calls():
    tree = ast.parse(SOURCE.read_text())
    return [node for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == 'insert_text']


def test_keypad_inserts_into_the_entry():
    assert _insert_text_calls(), 'the keypad must insert text somewhere'


def test_insert_text_uses_the_two_argument_signature():
    for call in _insert_text_calls():
        assert len(call.args) == 2, (
            'Gtk.Editable.insert_text takes (text, position); '
            'a third argument raises TypeError at runtime')


def test_insert_text_position_is_not_none():
    for call in _insert_text_calls():
        position = call.args[1]
        assert not (isinstance(position, ast.Constant) and position.value is None)
