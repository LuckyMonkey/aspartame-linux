"""Journal row edits must reflect what the datastore actually stored."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "gtk4-overlay/src/jarabe/journal/listview.py").read_text()
TREE = ast.parse(SOURCE)


def _method(name):
    node = next(n for n in ast.walk(TREE) if isinstance(n, ast.FunctionDef) and n.name == name)
    return ast.get_source_segment(SOURCE, node)



def test_keep_metadata_updates_only_in_the_success_callback():
    keep = _method("_keep_toggled")
    applied = keep.split("def applied", 1)[1].split("\n        try:", 1)[0]
    assert "metadata.update(updated)" in applied
    assert keep.count("metadata.update(updated)") == 1


def test_keep_failure_restores_without_reentering_the_handler():
    keep = _method("_keep_toggled")
    assert "handler_block_by_func(self._keep_toggled)" in keep
    assert "handler_unblock_by_func(self._keep_toggled)" in keep
    assert "self._is_current(uid, 'keep', revision)" in keep


def test_title_editor_closes_only_after_the_write_is_confirmed():
    title = _method("_finish_title")
    applied = title.split("def applied", 1)[1].split("def failed", 1)[0]
    assert "metadata.update(updated)" in applied
    assert "title_entry.set_visible(False)" in applied
    assert title.count("title_entry.set_visible(False)") == 1
    failed = title.split("def failed", 1)[1].split("\n        try:", 1)[0]
    assert "set_visible" not in failed  # the draft stays open for retry
