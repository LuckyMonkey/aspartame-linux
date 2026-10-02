from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_write_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-write-activity"
    info = (package / "activity/activity.info").read_text(); source = (package / "writeactivity4.py").read_text()
    assert "bundle_id = org.sugarlabs.Write" in info
    assert "sugar-activity4 writeactivity4.WriteActivity" in info
    assert "class WriteActivity(SimpleActivity)" in source
    assert "Document text" in source and "Save draft" in source
    assert "def read_file(self, file_path)" in source
    assert "def write_file(self, file_path)" in source
    assert "Path(file_path).read_text(encoding=\"utf-8\")" in source
    # Plain documents stay plain UTF-8; formatted ones become marked HTML.
    assert "Path(file_path).write_text(payload, encoding=\"utf-8\")" in source
    assert "FORMAT_MARKER" in source
    assert "self.save()" in source
    assert "org.sugarlabs.Write" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-write-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-write-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()


def test_write_formatting_roundtrip_undo_and_find():
    import os
    import subprocess
    import sys

    import pytest
    if not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        pytest.skip("no display for GTK4")
    root = Path(__file__).resolve().parents[1]
    run = subprocess.run([sys.executable, str(root / "tests/gtk4_harness/write_formatting.py")],
                         capture_output=True, text=True, timeout=120)
    assert run.returncode == 0, run.stderr[-4000:]
    assert "write-formatting=PASS" in run.stdout
