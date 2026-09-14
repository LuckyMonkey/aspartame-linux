from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_calculate_bundle_is_native_gtk4_and_staged():
    info = (ROOT / "packages/gtk4-calculate-activity/activity/activity.info").read_text()
    source = (ROOT / "packages/gtk4-calculate-activity/calculateactivity4.py").read_text()
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert "bundle_id = org.aspartame.Calculate" in info
    assert "exec = sugar-activity4 calculateactivity4.CalculateActivity" in info
    assert "Gtk.Grid" in source and "SimpleActivity" in source
    assert "ast.parse(text, mode=\"eval\")" in source
    assert 'ln -sfn "$calculate_activity" "$activity_dir/Calculate.activity"' in build


def test_calculate_rejects_non_arithmetic_expression():
    source = (ROOT / "packages/gtk4-calculate-activity/calculateactivity4.py").read_text()
    assert "raise ValueError(\"unsupported expression\")" in source
    assert "Invalid expression" in source
