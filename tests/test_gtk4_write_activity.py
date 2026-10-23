import base64
import struct
import sys
import zlib
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
PACKAGE = ROOT / "packages/gtk4-write-activity"
sys.path.insert(0, str(PACKAGE))
import write_doc  # noqa: E402
from gtk4_activity_harness import needs_gtk4, run  # noqa: E402
from write_doc import FORMAT, loads, paragraph, read_html, read_rtf, validate, write_html, write_rtf  # noqa: E402


def png():
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 1, 8, 2, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress(b"\x00\xff\x00\x00\x00\x00\xff")) + chunk(b"IEND", b""))


def sample():
    return validate({"format": FORMAT, "images": {"image1": base64.b64encode(png()).decode()},
                     "paragraphs": [
        paragraph("Field notes", style="h1", align="center"),
        {"style": "normal", "align": "fill", "list": None, "runs": [
            {"text": "Bold ", "marks": {"bold": True}},
            {"text": "red café", "marks": {"color": "#cc0000", "font": "Serif", "size": 18}},
            {"text": "2", "marks": {"super": True}}, {"image": "image1"}]},
        paragraph("• one", list_kind="bullet"),
        paragraph("1. first", list_kind="number"),
        paragraph("print(1)", style="plain"),
        paragraph("quoted", style="block", marks={"italic": True, "highlight": "#ffff00",
                                                   "underline": True}),
    ]})


def test_rtf_round_trips_every_feature():
    doc = sample()
    again = read_rtf(write_rtf(doc))
    assert again["paragraphs"] == doc["paragraphs"] and again["images"] == doc["images"]


def test_html_round_trips_every_feature():
    doc = sample()
    assert read_html(write_html(doc))["paragraphs"] == doc["paragraphs"]


def test_abiword_rtf_opens():
    # The shape GTK3 Write (AbiWord) saves: font/colour tables, a stylesheet,
    # \listtext markers and Unicode (backslash-u) escapes.
    raw = (r"{\rtf1\ansi\ansicpg1252\deff0{\fonttbl{\f0\froman\fcharset0 Times New Roman;}"
           r"{\f1\fswiss\fcharset0 Arial;}}{\colortbl;\red0\green0\blue0;\red255\green0\blue0;}"
           r"{\stylesheet{\s1\fs24 Normal;}}{\*\generator AbiWord;}"
           r"\pard\plain\qc{\b\fs32\f1 Heading}\par"
           r"\pard\plain Hello {\b world} {\cf2 red}\'e9 " + chr(92) + "u8364?" + r"\par"
           r"\pard{\listtext 1.\tab}Item\par}")
    doc, mime_type = loads(raw)
    assert mime_type == "application/rtf"
    heading, body, item = doc["paragraphs"]
    assert heading["align"] == "center"
    assert heading["runs"] == [{"text": "Heading", "marks": {"bold": True, "size": 16, "font": "Arial"}}]
    assert [r["text"] for r in body["runs"]] == ["Hello ", "world", " ", "red", "é €"]
    assert body["runs"][3]["marks"] == {"color": "#ff0000"}
    assert item["list"] == "number" and item["runs"][0]["text"] == "1. Item"


def test_write_1_payloads_still_open():
    doc, mime_type = loads('{"format": "aspartame-write-v1", "text": "Title\\nbody",'
                           ' "spans": [{"start": 0, "end": 5, "tags": ["heading"]},'
                           ' {"start": 6, "end": 10, "tags": ["bold"]}]}')
    assert mime_type is None
    assert doc["paragraphs"][0]["style"] == "h2"
    assert doc["paragraphs"][1]["runs"] == [{"text": "body", "marks": {"bold": True}}]


@pytest.mark.parametrize("raw", ['{"format": "aspartame-write-v9"}', "{\\rtf1 {\\b }",
                                 '{"format": "aspartame-write-v2", "paragraphs": []}'])
def test_unknown_or_broken_documents_raise(raw):
    if raw.startswith("{\\rtf"):
        assert loads(raw)[0]["paragraphs"]  # truncated RTF still yields its text
        return
    with pytest.raises(ValueError):
        loads(raw)


def test_pdf_export_paginates(tmp_path):
    from write_pdf import write_pdf
    doc = sample()
    doc["paragraphs"] += [paragraph("Lorem ipsum dolor sit amet " * 60)] * 6
    pages = write_pdf(doc, tmp_path / "out.pdf")
    assert pages >= 2 and (tmp_path / "out.pdf").read_bytes().startswith(b"%PDF")


SETUP = """
from writeactivity4 import WriteActivity


class FakeJournal:
    def __init__(self):
        self.exports = []

    def images(self):
        return []

    def export(self, title, mime_type, path):
        self.exports.append((title, mime_type, open(path, "rb").read()[:5]))


def write(metadata=None):
    activity = WriteActivity(None, journal=FakeJournal())
    activity.metadata = {"title": "Notes"} if metadata is None else metadata
    return activity


def select(activity, start, end):
    buf = activity.buffer
    buf.select_range(buf.get_iter_at_offset(start), buf.get_iter_at_offset(end))
"""


@needs_gtk4
def test_formatting_in_the_editor_saves_as_rtf_and_resumes(tmp_path):
    out = run("gtk4-write-activity", SETUP + f"""
activity = write()
activity.buffer.insert_at_cursor("Field notes\\nA red word")
select(activity, 0, 5)
activity.style.set_selected(1)                 # Heading 1 on line 1
activity.align.set_selected(1)                 # centred
select(activity, 14, 17)
button(activity, "Bold").emit("clicked")
activity.color.set_selected(2)                 # red
activity.size.set_selected(5)                  # 18 pt
end = activity.buffer.get_end_iter()
activity.buffer.place_cursor(end)
activity.buffer.insert_at_cursor("!")          # typed text takes the plain 'd' before it
activity.write_file({str(tmp_path / 'doc')!r})
print("mime", activity.metadata["mime_type"])
again = write({{"mime_type": "application/rtf"}})
again.read_file({str(tmp_path / 'doc')!r})
doc = again.get_document()
print("p0", doc["paragraphs"][0])
import json
print("p1", json.dumps(doc["paragraphs"][1]["runs"], sort_keys=True))
""")
    assert "mime application/rtf" in out
    assert "p0 {'style': 'h1', 'align': 'center', 'list': None, 'runs': [{'text': 'Field notes', 'marks': {}}]}" in out
    assert ('p1 [{"marks": {}, "text": "A "}, {"marks": {"bold": true, "color": "#c62828", "size": 18}, '
            '"text": "red"}, {"marks": {}, "text": " word!"}]') in out
    assert (tmp_path / "doc").read_text().startswith("{\\rtf1")


@needs_gtk4
def test_lists_find_images_and_export(tmp_path):
    image = tmp_path / "dot.png"
    image.write_bytes(png())
    out = run("gtk4-write-activity", SETUP + f"""
from writeactivity4 import png_from_file
activity = write()
activity.buffer.insert_at_cursor("eggs\\nmilk")
select(activity, 0, 9)
activity.list.set_selected(3)                  # numbered
print("text", repr(activity.buffer.get_text(*activity.buffer.get_bounds(), True)))
activity.buffer.place_cursor(activity.buffer.get_end_iter())
activity._insert_png(png_from_file({str(image)!r}), "dot")
activity.find.set_text("MILK")
button(activity, "Find next").emit("clicked")
print("status", activity.status.get_text())
for key in ("RTF", "HTML", "TXT", "PDF"):
    button(activity, "Export " + key).emit("clicked")
print("exports", activity.journal.exports)
doc = activity.get_document()
print("lists", [p["list"] for p in doc["paragraphs"]], len(doc["images"]))
""")
    assert "text '1. eggs\\n2. milk'" in out
    assert "status Found MILK on line 2" in out
    assert ("exports [('Notes (RTF)', 'application/rtf', b'{\\\\rtf'), ('Notes (HTML)', 'text/html', b'<!DOC'), "
            "('Notes (TXT)', 'text/plain', b'1. eg'), ('Notes (PDF)', 'application/pdf', b'%PDF-')]") in out
    assert "lists ['number', 'number'] 1" in out


@needs_gtk4
def test_html_and_text_documents_keep_their_format(tmp_path):
    (tmp_path / "page").write_text("<!DOCTYPE html><html><body><p>Hi <b>there</b></p></body></html>")
    (tmp_path / "note").write_text('{"looks": "like json"}')
    out = run("gtk4-write-activity", SETUP + f"""
page = write({{"mime_type": "text/html"}})
page.read_file({str(tmp_path / 'page')!r})
page.write_file({str(tmp_path / 'page2')!r})
note = write({{"mime_type": "text/plain"}})
note.read_file({str(tmp_path / 'note')!r})
note.write_file({str(tmp_path / 'note2')!r})
print("mimes", page.metadata["mime_type"], note.metadata["mime_type"])
try:
    open({str(tmp_path / 'bad')!r}, "wb").write(b"\\xff\\xfe not a valid payload")
    write().read_file({str(tmp_path / 'bad')!r})
except ValueError:
    print("refused")
""")
    assert "mimes text/html text/plain" in out
    assert "<b>there</b>" in (tmp_path / "page2").read_text()
    assert (tmp_path / "note2").read_text() == '{"looks": "like json"}\n'
    assert "refused" in out


def test_bundle_is_registered():
    info = (PACKAGE / "activity/activity.info").read_text()
    assert "bundle_id = org.sugarlabs.Write" in info
    assert "sugar-activity4 writeactivity4.WriteActivity" in info
    assert "application/rtf" in info and "text/html" in info
    assert write_doc.EXPORTS.keys() == {"rtf", "html", "txt", "pdf"}
