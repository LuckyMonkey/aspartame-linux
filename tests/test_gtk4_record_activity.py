import os
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
PACKAGE = ROOT / "packages/gtk4-record-activity"
PROBE = ROOT / "tests/gtk4_harness/record_capture.py"


def _capture_stack_usable():
    if not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        return False
    probe = ("import gi; gi.require_version('Gtk', '4.0'); gi.require_version('Gst', '1.0'); "
             "from gi.repository import Gst, Gtk; Gst.init(None); Gtk.Window(); "
             "assert all(Gst.ElementFactory.find(n) for n in ('videotestsrc', 'audiotestsrc', "
             "'pngenc', 'vp8enc', 'webmmux', 'opusenc', 'oggmux'))")
    return subprocess.run([sys.executable, "-c", probe], capture_output=True).returncode == 0


def test_record_is_a_native_gtk4_bundle_under_the_original_identity():
    info = (PACKAGE / "activity/activity.info").read_text()
    assert "bundle_id = org.laptop.RecordActivity" in info
    assert "exec = sugar-activity4 recordactivity4.RecordActivity" in info
    assert (PACKAGE / "activity/activity-record.svg").is_file()
    source = (PACKAGE / "recordactivity4.py").read_text()
    assert 'require_version("Gtk", "3.0")' not in source
    assert "def read_file(self, file_path)" in source
    assert "def write_file(self, file_path)" in source


def test_record_is_registered_for_build_sync_and_lifecycle_matrix():
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    assert 'ln -sfn "$record_activity" "$activity_dir/Record.activity"' in build
    sync = (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert sync.count("gtk4-record-activity") >= 3
    matrix = (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "'org.laptop.RecordActivity|recordactivity4.RecordActivity'" in matrix


def test_record_guest_probe_seeds_and_verifies_a_capture():
    probe = (ROOT / "scripts/sugar-gtk4-record-roundtrip.py").read_text()
    assert 'BUNDLE_ID = "org.laptop.RecordActivity"' in probe
    assert "journal.LaunchBundle(BUNDLE_ID, object_id)" in probe
    assert 'archive.read("media/photo-1.png") == tiny_png()' in probe
    assert "record-roundtrip=PASS" in probe


@pytest.mark.skipif(not _capture_stack_usable(),
                    reason="GTK4, a display, or GStreamer test elements are unavailable")
def test_record_captures_photo_video_audio_and_resumes_them():
    run = subprocess.run([sys.executable, str(PROBE)], capture_output=True,
                         text=True, timeout=180)
    assert run.returncode == 0, run.stderr[-4000:]
    assert "record-capture=PASS" in run.stdout
