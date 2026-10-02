"""Run every native GTK4 Activity bundle through the headless harness.

Each bundle runs in its own process (see ``gtk4_harness/roundtrip.py``) so the
GTK4 namespace never meets the GTK3 tests in this pytest process.  This is
host-side behavioral evidence for construction, button callbacks, and Journal
save/resume stability; it does not replace the guest round-trip probes.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tests/gtk4_harness/roundtrip.py"
BUNDLES = sorted(p for p in (ROOT / "packages").glob("gtk4-*-activity")
                 if (p / "activity/activity.info").is_file())


def _gtk4_usable():
    if not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        return False
    probe = ("import gi; gi.require_version('Gtk', '4.0'); "
             "from gi.repository import Gtk; Gtk.Window()")
    return subprocess.run([sys.executable, "-c", probe],
                          capture_output=True).returncode == 0


GTK4 = _gtk4_usable()


def test_harness_discovers_bundles():
    assert len(BUNDLES) >= 48


@pytest.mark.skipif(not GTK4, reason="GTK4 introspection or a display is unavailable")
@pytest.mark.parametrize("bundle", BUNDLES, ids=lambda p: p.name)
def test_activity_constructs_clicks_and_resumes(bundle):
    run = subprocess.run([sys.executable, str(RUNNER), str(bundle)],
                         capture_output=True, text=True, timeout=120)
    assert run.returncode == 0, run.stderr[-4000:]
    result = json.loads(run.stdout.strip().splitlines()[-1])
    assert result["checks"]["construct"]
    assert not result["errors"], "\n".join(result["errors"])
    if result["checks"]["persistent"]:
        assert result["checks"]["roundtrip_stable"]
        assert result["checks"]["malformed_tolerated"]
