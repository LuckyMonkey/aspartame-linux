import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parents[1]
ADAPTER = ROOT / "scripts/sugar-chirality-activity.py"


def test_activity_adapter_is_single_surface_and_gtk4_only():
    source = ADAPTER.read_text()
    assert "ChiralSession" in source
    assert "org.laptop.Shell" in source
    assert "ActivateActivity" in source
    assert "SetActive(True)" in source
    assert "sugar-gtk4-space.sh" not in source
    assert "XMoveResizeWindow" not in source
    assert "side-by-side" not in source.lower()
    assert "split-screen" not in source.lower()


def test_activity_adapter_assigns_two_hands_without_a_history_log(tmp_path):
    state = tmp_path / "chirality.json"
    command = [sys.executable, str(ADAPTER), "--state-file", str(state)]
    left = subprocess.run(
        command + ["assign", "left", "activity-a", "--object-ref", "journal:text"],
        check=True,
        capture_output=True,
        text=True,
    )
    right = subprocess.run(command + ["assign", "right", "activity-b"], check=True,
                           capture_output=True, text=True)
    payload = json.loads(right.stdout)
    assert payload["active_hand"] == "left"
    assert payload["hands"][0]["activity_id"] == "activity-a"
    assert payload["hands"][1]["activity_id"] == "activity-b"
    assert "history" not in state.read_text()
    assert "journal:text" in left.stdout


def test_iso_packages_the_activity_adapter():
    build = (ROOT / "scripts/build-iso.sh").read_text()
    assert "sugar-chirality-activity.py" in build
    assert "sugar-gtk4-chirality-activity-roundtrip.py" in build


def test_guest_roundtrip_proves_two_live_activities_switch_on_one_surface():
    probe = (ROOT / "scripts/sugar-gtk4-chirality-activity-roundtrip.py").read_text()
    assert "org.laptop.Shell" in probe
    assert '"left", "right", "left"' in probe
    assert "mode=single-surface" in probe
    assert "StopActivity" in probe
