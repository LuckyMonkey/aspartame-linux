"""Concurrent Chirality writers must not lose each other's updates."""
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from aspartame_chirality import Hand, Side  # noqa: E402
import chirality_state  # noqa: E402


def test_concurrent_updates_keep_both_changes(tmp_path):
    state = tmp_path / "chirality.json"

    def slow_left(session):
        session.assign(Side.LEFT, Hand("left-activity", None, None, "org.left"))
        time.sleep(0.3)  # a slow writer holding a stale snapshot without a lock

    def right(session):
        session.assign(Side.RIGHT, Hand("right-activity", None, None, "org.right"))

    first = threading.Thread(target=chirality_state.update, args=(state, slow_left))
    first.start()
    time.sleep(0.05)
    chirality_state.update(state, right)
    first.join()

    session = chirality_state.load(state)
    assert session.get(Side.LEFT).activity_id == "left-activity"
    assert session.get(Side.RIGHT).activity_id == "right-activity"


def test_a_failed_mutation_writes_nothing(tmp_path):
    state = tmp_path / "chirality.json"
    chirality_state.update(state, lambda s: s.assign(
        Side.LEFT, Hand("kept", None, None, "org.kept")))
    before = state.read_bytes()

    def refuse(session):
        session.release(Side.LEFT)
        raise RuntimeError("abandon")

    try:
        chirality_state.update(state, refuse)
    except RuntimeError:
        pass
    assert state.read_bytes() == before
    assert not [p for p in tmp_path.iterdir() if p.name.startswith(".chirality.json.") and p.suffix != ".lock"]


def test_resume_reports_each_hand_and_recognises_live_ones():
    resume = (ROOT / "scripts/sugar-gtk4-chirality-session-resume.py").read_text()
    assert "chirality-resume={status}" in resume
    assert '"PARTIAL" if restored' in resume
    assert "Already restored by an earlier attempt" in resume
    assert "DBUS_SESSION_BUS_ADDRESS" in resume
    assert "resume-tmp" not in resume
