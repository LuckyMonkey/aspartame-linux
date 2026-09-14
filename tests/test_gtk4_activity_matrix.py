from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_activity_matrix_covers_registered_modern_bundles():
    probe = (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    for bundle in ("org.laptop.HelpActivity", "org.aspartame.Count",
                   "org.aspartame.Calculate", "org.laptop.ImageViewerActivity",
                   "org.laptop.Terminal", "org.laptop.WebActivity",
                   "org.laptop.Log"):
        assert bundle in probe
    assert "activity-matrix=PASS" in probe
