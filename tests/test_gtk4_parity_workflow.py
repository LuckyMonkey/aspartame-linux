import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("parity", ROOT / "scripts/sugar-parity.py")
parity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parity)


def _report(tmp_path, scores):
    text = parity.TEMPLATE.read_text()
    text = text.replace("{{BUNDLE_ID}}", "org.sugarlabs.Write").replace("{{DATE}}", "2026-10-02")
    lines = []
    steps = iter(scores)
    for line in text.splitlines():
        if parity.STEP_ROW.match(line):
            line = line.rstrip()[:-1].rstrip() + " %s |" % next(steps, "")
        lines.append(line)
    path = tmp_path / "write.md"
    path.write_text("\n".join(lines) + "\n")
    return path


def test_parity_data_is_current():
    assert parity.main(["check"]) == 0


def test_every_gtk4_activity_has_a_pair_and_reference():
    pairs = parity.read_pairs()
    packages = list(ROOT.glob("packages/gtk4-*-activity/activity/activity.info"))
    assert len(pairs) == len(packages) + len(parity.PINNED_GTK4)
    assert all(row["gtk3_reference"] != "none recorded" for row in pairs.values())
    assert pairs["org.laptop.RecordActivity"]["gtk3_reference"] == "sugar-activity-record"


def test_report_score_is_its_worst_step(tmp_path):
    report = parity.parse_report(_report(tmp_path, [0, 2, 0, 6, 0, 2, 0, 0]))
    assert report["bundle_id"] == "org.sugarlabs.Write"
    assert report["score"] == 6 and report["scored"] == 8


def test_unscored_step_keeps_report_in_progress(tmp_path):
    report = parity.parse_report(_report(tmp_path, [0, 0, 0]))
    assert report["score"] is None and report["scored"] == 3 and report["steps"] == 8


def test_off_scale_score_does_not_count(tmp_path):
    report = parity.parse_report(_report(tmp_path, [0, 0, 0, 0, 0, 0, 0, 5]))
    assert report["score"] is None


def _gtk4_usable():
    if not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        return False
    probe = ("import gi; gi.require_version('Gtk', '4.0'); "
             "from gi.repository import Gtk; Gtk.Window()")
    return subprocess.run([sys.executable, "-c", probe], capture_output=True).returncode == 0


@pytest.mark.skipif(not _gtk4_usable(), reason="GTK4 introspection or a display is unavailable")
def test_activity_manager_face_ratings_keep_classic_answers():
    run = subprocess.run([sys.executable, str(ROOT / "tests/gtk4_harness/activity_manager_probe.py")],
                         capture_output=True, text=True, timeout=120)
    assert run.returncode == 0, run.stderr[-4000:]
    assert "activity-manager-faces=PASS" in run.stdout
