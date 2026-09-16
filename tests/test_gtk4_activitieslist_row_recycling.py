"""Home's List View factory callbacks must tolerate a recycled row.

GTK4 may unset a list item's child before the unbind/teardown callbacks run.
Calling unbind() unconditionally raised
AttributeError: 'NoneType' object has no attribute 'unbind'
every time the list recycled rows.
"""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'gtk4-overlay/src/jarabe/desktop/activitieslist.py'


def _function(name):
    tree = ast.parse(SOURCE.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError('%s not found' % name)


def _guards_none(node):
    """Whether the function tests its row against None before using it."""
    return any(
        isinstance(sub, ast.Compare)
        and any(isinstance(c, ast.Constant) and c.value is None
                for c in sub.comparators)
        for sub in ast.walk(node))


def test_teardown_guards_a_missing_row():
    assert _guards_none(_function('_teardown_row'))


def test_unbind_guards_a_missing_row():
    assert _guards_none(_function('_unbind_row'))


def test_teardown_still_discards_the_row_it_tore_down():
    # The guard must not drop the bookkeeping for real rows.
    body = ast.unparse(_function('_teardown_row'))
    assert '_rows.discard' in body
    assert 'unbind()' in body
