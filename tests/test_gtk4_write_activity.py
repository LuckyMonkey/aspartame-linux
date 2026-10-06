from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_write_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-write-activity"
    info = (package / "activity/activity.info").read_text(); source = (package / "writeactivity4.py").read_text()
    assert "bundle_id = org.sugarlabs.Write" in info
    assert "sugar-activity4 writeactivity4.WriteActivity" in info
    assert "class WriteActivity(SimpleActivity)" in source
    assert "Document text" in source and "Save draft" in source
    assert "document_frame" in source and "Gtk.Frame(label=\"Document\")" in source
    assert "root.append(document_frame)" in source
    assert "ScrolledWindow" in source
    assert "Gtk.Overlay" in source and "Start writing your document" in source
    assert "controls.set_halign(Gtk.Align.END)" in source
    assert "buffer.connect(\"changed\", self._document_changed)" in source
    assert "Gtk.EventControllerKey" in source and "_format_key" in source
    assert "GTK4 returns an empty tuple" in source
    assert 'button = Gtk.Button(label=label)' in source
    assert '"aspartame-write-v1"' in source and '"spans"' in source
    assert "_format_spans" in source and "_set_document" in source
    assert "def read_file(self, file_path)" in source
    assert "def write_file(self, file_path)" in source
    assert "Path(file_path).read_text(encoding=\"utf-8\")" in source
    assert "Path(file_path).write_text(text, encoding=\"utf-8\")" in source
    assert "self.save()" in source
    assert "org.sugarlabs.Write" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-write-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-write-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()


def test_write_format_probe_qualifies_persistent_rich_text():
    probe = (ROOT / "scripts/sugar-gtk4-write-format-roundtrip.py").read_text()
    assert "Select all action" in probe
    assert "aspartame-write-v1" in probe
    assert "read-interoperability=PASS" in probe
