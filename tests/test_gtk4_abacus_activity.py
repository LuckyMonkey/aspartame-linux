from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_abacus_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-abacus-activity"
    info = (package / "activity/activity.info").read_text(); source = (package / "abacusactivity4.py").read_text()
    assert "bundle_id = com.homegrownapps.abacus" in info
    assert "sugar-activity4 abacusactivity4.AbacusActivity" in info
    assert "class AbacusActivity(SimpleActivity)" in source
    assert "place value" in source and 'label="Clear"' in source
    assert "Click a bead" in source and "_set_digit" in source
    assert 'Gtk.Frame(label="Place-value rods")' in source
    assert "rods_frame.set_halign(Gtk.Align.CENTER)" in source
    assert "row.set_halign(Gtk.Align.CENTER)" in source
    assert "self._beads = []" in source
    assert "def _render_beads" in source
    assert 'button.abacus-bead' in source and 'font-size: 20px' in source
    assert 'rods_frame.set_size_request(760, -1)' in source
    assert 'value_frame.set_size_request(420, -1)' in source
    assert 'label.abacus-title' in source
    assert 'clear.set_halign(Gtk.Align.CENTER)' in source
    assert "com.homegrownapps.abacus" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-abacus-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-abacus-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()


def test_abacus_journal_roundtrip_is_json():
    source = (ROOT / "packages/gtk4-abacus-activity/abacusactivity4.py").read_text()
    probe = (ROOT / "scripts/sugar-gtk4-abacus-roundtrip.py").read_text()
    assert "def read_file(self, file_path)" in source
    assert "def write_file(self, file_path)" in source
    assert '"values"' in source
    assert "direct-bead-action=PASS" in probe
    assert "Move the 7th bead on the Ones rod" in probe
