from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_portfolio_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-portfolio-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "portfolioactivity4.py").read_text()
    assert "bundle_id = org.sugarlabs.PortfolioActivity" in info
    assert "sugar-activity4 portfolioactivity4.PortfolioActivity" in info
    assert "class PortfolioActivity(SimpleActivity)" in source
    assert "Save draft" in source
    assert "self.save()" in source
    assert "Gtk.ScrolledWindow" in source and "Project description" in source
    assert "Gtk.Overlay" in source and "Describe the project" in source
    assert "controls.set_halign(Gtk.Align.END)" in source
    assert "self.body.get_buffer().connect(\"changed\", self._body_changed)" in source
    assert "root.append(body_frame)" in source
    assert 'frame.project-pane' in source
    assert "org.sugarlabs.PortfolioActivity" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()


def test_portfolio_journal_roundtrip_is_json():
    source = (ROOT / "packages/gtk4-portfolio-activity/portfolioactivity4.py").read_text()
    assert "def read_file(self, file_path)" in source
    assert "def write_file(self, file_path)" in source
    assert '"title"' in source and '"body"' in source
    assert "gtk4-portfolio-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-portfolio-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
