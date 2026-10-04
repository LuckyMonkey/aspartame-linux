from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_finance_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-finance-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "financeactivity4.py").read_text()
    assert "bundle_id = org.laptop.community.Finance" in info
    assert "sugar-activity4 financeactivity4.FinanceActivity" in info
    assert "class FinanceActivity(SimpleActivity)" in source
    assert "Add income" in source and "Add expense" in source
    assert "org.laptop.community.Finance" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-finance-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-finance-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()


def test_finance_journal_roundtrip_is_json():
    source = (ROOT / "packages/gtk4-finance-activity/financeactivity4.py").read_text()
    assert "def read_file(self, file_path)" in source
    assert "def write_file(self, file_path)" in source
    assert '"transactions"' in source


def test_finance_transactions_use_aligned_description_and_amount_columns():
    source = (ROOT / "packages/gtk4-finance-activity/financeactivity4.py").read_text()
    assert "Gtk.Clamp" not in source
    assert "root.set_hexpand(True); root.set_vexpand(True)" in source
    assert "body.set_hexpand(True)" in source
    assert "body.set_halign(Gtk.Align.FILL)" in source
    assert "body.set_valign(Gtk.Align.FILL)" in source
    assert "form = Gtk.Grid(column_spacing=12, row_spacing=6)" in source
    assert "form.attach(self.description, 0, 1, 1, 1)" in source
    assert "form.attach(self.amount, 1, 1, 1, 1)" in source
    assert 'description_heading = Gtk.Label(label="Description"' in source
    assert 'amount_heading = Gtk.Label(label="Amount"' in source
    assert 'table_row.attach(amount_label, 1, 0, 1, 1)' in source
    assert 'No transactions yet. Add income or an expense to begin.' in source
    assert 'self.empty_state.set_visible(False)' in source
