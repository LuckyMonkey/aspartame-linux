import json
import sys
from fractions import Fraction
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
PACKAGE = ROOT / "packages/gtk4-abacus-activity"
sys.path.insert(0, str(PACKAGE))
from abacus_model import Abacus, TYPE_ORDER, format_value, parse_value  # noqa: E402
from gtk4_activity_harness import needs_gtk4, run  # noqa: E402

# The abacus types of the GTK3 reference (sugarlabs/abacus AbacusActivity.py),
# minus 'fraction', which its toolbar leaves commented out.
GTK3_TYPES = {"suanpan", "soroban", "decimal", "nepohualtzintzin", "hexadecimal",
              "binary", "schety", "caacupe", "cuisenaire", "custom"}


def test_every_gtk3_abacus_type_is_available():
    assert set(TYPE_ORDER) == GTK3_TYPES


@pytest.mark.parametrize("kind,number,rods", [
    ("suanpan", 1234, [[0, 1], [0, 2], [0, 3], [0, 4]]),
    ("soroban", Fraction("3.25"), None),
    ("hexadecimal", 255, [[1, 7], [1, 7]]),
    ("binary", 5, [[0, 1], [0, 0], [0, 1]]),
    ("nepohualtzintzin", 399, [[3, 4], [3, 4]]),
    ("schety", Fraction("12.75"), None),
    ("caacupe", Fraction(7, 3), None),
    ("cuisenaire", Fraction(1, 2), None),
])
def test_numbers_round_trip_on_each_type(kind, number, rods):
    abacus = Abacus(kind)
    abacus.set_value(number)
    assert abacus.value() == number
    if rods:
        assert abacus.rods[-len(rods):] == rods
    again = Abacus.from_payload(json.loads(json.dumps(abacus.to_payload())))
    assert again.value() == number and again.type.name == kind


def test_bead_clicks_follow_the_reference_rules():
    abacus = Abacus("suanpan")
    abacus.click_bead(14, "bottom", 2)      # push three lower beads up
    abacus.click_bead(14, "top", 0)         # one upper bead down: +5
    assert abacus.value() == 8
    abacus.click_bead(14, "bottom", 0)      # first bead back: the rest follow
    assert abacus.value() == 5
    fractions = Abacus("caacupe")
    fractions.click_bead(6, "bottom", 0, down=True)   # 1/2 rod, two beads
    assert fractions.value() == Fraction(-1)
    fractions.click_bead(6, "bottom", 0)              # upper bead back to rest
    assert fractions.value() == Fraction(-1, 2)


def test_values_display_exactly():
    assert format_value(Fraction("12.75")) == "12.75"
    assert format_value(Fraction(7, 3)) == "2 1/3"
    assert format_value(Fraction(-1, 2), fractional=True) == "−1/2"
    assert parse_value("2 1/3") == Fraction(7, 3)
    assert parse_value("1,234") == 1234
    with pytest.raises(ValueError):
        parse_value("twelve")


def test_numbers_that_do_not_fit_are_refused():
    with pytest.raises(ValueError):
        Abacus("binary").set_value(1 << 15)
    with pytest.raises(ValueError):
        Abacus("decimal").set_value(Fraction(1, 2))


@pytest.mark.parametrize("payload", [
    [], {"format": "other"}, {"format": "aspartame-abacus-v2", "type": "suanpan",
                              "custom": {}, "rods": []},
    {"values": [0, 1, 2, 3, 99]},
])
def test_malformed_payloads_raise(payload):
    with pytest.raises(ValueError):
        Abacus.from_payload(payload)


def test_gtk4_abacus_1_payload_still_opens():
    abacus = Abacus.from_payload({"values": [0, 1, 2, 3, 4]})
    assert abacus.type.name == "decimal" and abacus.value() == 1234


@needs_gtk4
def test_activity_shows_typed_number_and_saves_it(tmp_path):
    out = run("gtk4-abacus-activity", f"""
        from abacusactivity4 import AbacusActivity
        from abacus_model import TYPE_ORDER
        activity = AbacusActivity(None)
        activity.kind.set_selected(TYPE_ORDER.index("soroban"))
        activity.entry.set_text("3.25")
        button(activity, "Show number").emit("clicked")
        print("shown", activity.value_label.get_text())
        activity.write_file({str(tmp_path / 'abacus.json')!r})
        restored = AbacusActivity(None)
        restored.read_file({str(tmp_path / 'abacus.json')!r})
        print("restored", restored.abacus.type.name, restored.value_label.get_text(),
              restored.kind.get_selected() == TYPE_ORDER.index("soroban"))
        try:
            open({str(tmp_path / 'bad')!r}, "wb").write(b"\\xff\\xfe not json")
            restored.read_file({str(tmp_path / 'bad')!r})
        except ValueError:
            print("refused")
    """)
    assert "shown 3.25" in out
    assert "restored soroban 3.25 True" in out
    assert "refused" in out


def test_bundle_is_registered():
    info = (PACKAGE / "activity/activity.info").read_text()
    assert "exec = sugar-activity4 abacusactivity4.AbacusActivity" in info
    assert "com.homegrownapps.abacus" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-abacus-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-abacus-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
