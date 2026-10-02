from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_activity_matrix_matches_native_activity_catalog():
    check = ROOT / "scripts/sugar-gtk4-activity-matrix-check.py"
    result = subprocess.run(
        [sys.executable, str(check)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "50 entries, 48 native, PASS" in result.stdout


def test_activity_matrix_covers_registered_modern_bundles():
    probe = (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    for bundle in ("org.laptop.HelpActivity", "org.aspartame.Count",
                   "org.aspartame.Calculate", "org.laptop.ImageViewerActivity",
                   "org.laptop.Terminal", "org.laptop.WebActivity",
                   "org.laptop.Log"):
        assert bundle in probe
    assert "activity-matrix=PASS" in probe
    assert 'cycles=${ACTIVITY_CYCLES:-3}' in probe
