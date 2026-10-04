import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import aspartame_chirality as chirality


def test_single_surface_space_bridge_keeps_spaces_and_chirality_separate():
    bridge = (ROOT / "scripts/sugar-chirality-space.sh").read_text()
    assert 'left)' in bridge
    assert 'right)' in bridge
    assert '"$switcher" gtk3' in bridge
    assert '"$switcher" gtk4' in bridge
    assert 'mode=single-surface' in bridge
    assert 'side-by-side' not in bridge
    assert 'geometry' not in bridge


def test_direct_hand_selection_preserves_each_activity_state():
    session = chirality.ChiralSession()
    session.assign(
        chirality.Side.LEFT,
        chirality.Hand("read", "journal:paper", "paper.pdf"),
    )
    session.assign(
        chirality.Side.RIGHT,
        chirality.Hand("write", "journal:notes", "notes"),
    )

    session.activate(chirality.Side.RIGHT)
    assert session.active_hand is chirality.Side.RIGHT
    session.activate(chirality.Side.LEFT)
    assert session.active_hand is chirality.Side.LEFT
    assert session.right_hand.object_ref == "journal:notes"


def test_third_activity_requires_explicit_replacement():
    session = chirality.ChiralSession()
    session.assign_first_free(chirality.Hand("a"))
    session.assign_first_free(chirality.Hand("b"))
    with pytest.raises(chirality.NoFreeHand):
        session.assign_first_free(chirality.Hand("c"))

    released = session.assign(
        chirality.Side.LEFT, chirality.Hand("c"), replace=True
    )
    assert released.activity_id == "a"
    assert session.left_hand.activity_id == "c"
    assert session.right_hand.activity_id == "b"


def test_crashed_hand_does_not_destroy_the_other_hand():
    session = chirality.ChiralSession()
    session.assign_first_free(chirality.Hand("active", "journal:a"))
    session.assign_first_free(chirality.Hand("held", "journal:b"))
    session.activate(chirality.Side.RIGHT)

    assert session.activity_exited("held") is chirality.Side.RIGHT
    assert session.left_hand.activity_id == "active"
    assert session.active_hand is chirality.Side.LEFT


def test_object_handoff_is_reference_only_and_has_no_history():
    session = chirality.ChiralSession()
    session.assign(
        chirality.Side.LEFT,
        chirality.Hand("reader", "journal:paper", "paper.pdf"),
    )
    session.assign(chirality.Side.RIGHT, chirality.Hand("writer"))
    session.handoff_object(chirality.Side.LEFT, chirality.Side.RIGHT)

    assert session.right_hand.object_ref == "journal:paper"
    assert session.to_dict().keys() == {
        "left_hand", "right_hand", "active_hand"
    }
    assert "history" not in json.dumps(session.to_dict())


def test_accessible_state_is_color_independent_and_explicit():
    session = chirality.ChiralSession()
    session.assign(chirality.Side.LEFT, chirality.Hand("reader"))
    state = session.accessible_state()
    assert state["hands"][0]["label"] == "Left Hand"
    assert state["hands"][0]["state"] == "active"
    assert state["hands"][1]["label"] == "Right Hand"
    assert state["hands"][1]["activity_id"] is None


def test_spaces_are_single_surface_selection_separate_from_hands():
    spaces = chirality.Spaces()
    assert spaces.current().space_id == "classic"
    selected = spaces.select("modern")
    assert selected.switch_target == "gtk4"
    assert spaces.accessible_state()["active_space"] == "modern"
    assert spaces.to_dict() == {"active_space": "modern"}


def test_spaces_do_not_store_activity_object_or_history_state():
    spaces = chirality.Spaces()
    spaces.select("modern")
    encoded = json.dumps(spaces.to_dict())
    assert "activity" not in encoded
    assert "object" not in encoded
    assert "history" not in encoded


def test_spaces_reject_unknown_selection():
    with pytest.raises(chirality.ChiralityError):
        chirality.Spaces().select("side-by-side")


def test_spaces_cli_records_only_current_full_surface(tmp_path):
    cli = ROOT / "scripts/sugar-chirality.py"
    state = tmp_path / "spaces.json"
    result = subprocess.run(
        [sys.executable, str(cli), "--spaces-state-file", str(state),
         "spaces-select", "modern"],
        check=True, capture_output=True, text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["active_space"] == "modern"
    assert payload["spaces"][1]["switch_target"] == "gtk4"
    assert json.loads(state.read_text())["active_space"] == "modern"
    assert "history" not in state.read_text()
