import struct
import sys
import zlib
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
PACKAGE = ROOT / "packages/gtk4-portfolio-activity"
sys.path.insert(0, str(PACKAGE))
from gtk4_activity_harness import needs_gtk4, run  # noqa: E402
from portfolio_model import Show, Slide  # noqa: E402


def png():
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 1, 8, 2, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress(b"\x00\xff\x00\x00\x00\x00\xff")) + chunk(b"IEND", b""))


def slides():
    return [Slide("a", "Kite", "We built a kite"), Slide("b", "Volcano"), Slide("c", "Poem")]


def test_scan_keeps_order_and_unsaved_edits():
    show = Show()
    show.load_starred(slides())
    show.go(2)
    assert show.move(-1) and [s.uid for s in show.slides] == ["a", "c", "b"]
    show.edit(title="Poems")
    show.load_starred(slides() + [Slide("d", "New")])
    assert [s.uid for s in show.slides] == ["a", "c", "b", "d"]
    assert show.slide.uid == "c" and show.slide.title == "Poems" and show.dirty() == [show.slide]


def test_navigation_and_unstar():
    show = Show()
    show.load_starred(slides())
    assert not show.step(-1) and show.step(1) and show.step(1) and not show.step(1)
    assert show.step(1, wrap=True) and show.current == 0
    show.remove("a")
    assert [s.uid for s in show.slides] == ["b", "c"] and show.slide.uid == "b"


def test_payload_round_trips():
    show = Show()
    show.title, show.introduction, show.interval = "My year", "Things I made", 30
    show.load_starred(slides())
    show.go(1)
    again = Show.from_payload(show.to_payload())
    assert (again.title, again.introduction, again.interval, again.order, again.current) == \
        ("My year", "Things I made", 30, ["a", "b", "c"], 1)


def test_gtk4_portfolio_1_text_becomes_the_cover():
    show = Show.from_payload({"title": "Science fair", "body": "What I learned"})
    assert (show.title, show.introduction) == ("Science fair", "What I learned")


@pytest.mark.parametrize("payload", [[], {"format": "other"}, {"title": 3},
                                     {"format": "aspartame-portfolio-v2", "interval": 7}])
def test_malformed_payloads_raise(payload):
    with pytest.raises(ValueError):
        Show.from_payload(payload)


def test_pdf_has_a_cover_and_a_page_per_slide(tmp_path):
    from portfolio_export import write_pdf
    pages = write_pdf(tmp_path / "p.pdf", "My year", "Intro", slides(), {"a": png()})
    assert pages == 4 and (tmp_path / "p.pdf").read_bytes().startswith(b"%PDF")


SETUP = """
import struct, zlib
from gi.repository import GLib
from portfolioactivity4 import PortfolioActivity
from portfolio_model import Slide


class FakeJournal:
    def __init__(self):
        self.updates, self.unstarred, self.exports = [], [], []
        self.entries = [Slide("a", "Kite", "We built a kite", "image/png"), Slide("b", "Volcano")]

    def starred(self):
        return [Slide(s.uid, s.title, s.description, s.mime_type) for s in self.entries
                if s.uid not in self.unstarred]

    def picture(self, slide):
        return b""

    def update(self, slide):
        self.updates.append((slide.uid, slide.title, slide.description))

    def unstar(self, uid):
        self.unstarred.append(uid)

    def export(self, title, mime_type, path):
        self.exports.append((title, mime_type, open(path, "rb").read(5)))


def portfolio():
    activity = PortfolioActivity(None, journal=FakeJournal())
    context = GLib.MainContext.default()
    while context.iteration(False):
        pass
    return activity
"""


@needs_gtk4
def test_slides_edit_back_to_the_journal_and_export(tmp_path):
    out = run("gtk4-portfolio-activity", SETUP + f"""
activity = portfolio()
print("counter", activity.counter.get_text(), activity.slide_title.get_text())
button(activity, "Next").emit("clicked")
activity.slide_title.set_text("Volcano model")
activity.description.get_buffer().set_text("It erupts")
activity.cover_title.set_text("My year")
button(activity, "Save as PDF").emit("clicked")
activity.write_file({str(tmp_path / 'portfolio')!r})
print("updates", activity.journal.updates)
print("exports", activity.journal.exports)
button(activity, "Unstar").emit("clicked")
print("after", activity.counter.get_text(), activity.journal.unstarred)
again = PortfolioActivity(None, journal=FakeJournal())
again.read_file({str(tmp_path / 'portfolio')!r})
print("resumed", again.cover_title.get_text(), again.counter.get_text())
try:
    open({str(tmp_path / 'bad')!r}, "wb").write(b"\\xff\\xfe not a valid payload")
    again.read_file({str(tmp_path / 'bad')!r})
except ValueError:
    print("refused")
""")
    assert "counter Slide 1 of 2 Kite" in out
    assert "updates [('b', 'Volcano model', 'It erupts')]" in out
    assert "exports [('My year (PDF)', 'application/pdf', b'%PDF-')]" in out
    assert "after Slide 1 of 1 ['b']" in out
    assert "resumed My year Slide 2 of 2" in out
    assert "refused" in out


def test_bundle_is_registered():
    info = (PACKAGE / "activity/activity.info").read_text()
    assert "bundle_id = org.sugarlabs.PortfolioActivity" in info
    assert "sugar-activity4 portfolioactivity4.PortfolioActivity" in info
    assert "org.sugarlabs.PortfolioActivity" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-portfolio-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-portfolio-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
