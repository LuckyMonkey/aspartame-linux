from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_gtk4_journal_list_uses_native_selection_api():
    source = (ROOT / "gtk4-overlay/src/jarabe/journal/listview.py").read_text()
    assert "Gtk.SelectionMode.MULTIPLE" in source
    assert "get_selected_rows()" in source
    assert "select_row(row)" in source
    assert "unselect_all()" in source
    assert "def get_model(self): return self" in source
    assert "def set_selected(self, uid, value):" in source
    assert "def get_metadata(self, uid):" in source
    assert "row.set_focusable(True)" in source
    assert "row.set_activatable(True)" in source
    assert "Gtk.CheckButton(label=_('Keep'))" in source
    assert "write_metadata(" in source
    assert "Gtk.Entry(text=title)" in source
    assert "Journal title updated" in source
    assert "Confirm delete" in source
    assert "model.delete(str(uid))" in source
    assert "project_label =" in source
    assert "get_selected_object_id()" in source
    assert "Journal project updated" in source
    assert "Project: %s" in source
    assert "def applied(*args):" in source
    assert "External volume: %s" in source
    assert "mountpoint" in source
    assert "Gtk.ToggleButton(label=_('Projects'))" in source
    assert "def get_projects_view_active(self): return self._projects_only" in source
    assert "if self._projects_only and not metadata.get('project_id')" in source
    assert "self._empty.set_visible(shown == 0)" in source
    assert "No Journal entries are assigned to a project" in source


def test_gtk4_journal_selection_emits_count_changes():
    source = (ROOT / "gtk4-overlay/src/jarabe/journal/listview.py").read_text()
    assert "selected-rows-changed" in source
    assert "self.emit('selection-changed', len(self.get_selected_items()))" in source


def test_gtk4_objectchooser_uses_native_journal_surface():
    source = (ROOT / "gtk4-overlay/src/jarabe/journal/objectchooser.py").read_text()
    assert "class ObjectChooser(Gtk.Window)" in source
    assert "'response'" in source
    assert "get_selected_object_id" in source
    assert "Gtk.SearchEntry" in source
    assert "ListView(None)" in source
    assert "from sugar3.graphics" not in source
