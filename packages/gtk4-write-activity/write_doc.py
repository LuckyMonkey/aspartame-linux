"""Write documents and their file formats, independent of GTK.

A document is a list of paragraphs::

    {"style": "normal"|"h1".."h4"|"block"|"plain",
     "align": "left"|"center"|"right"|"fill",
     "list": None|"bullet"|"dash"|"number"|"lower"|"upper",
     "runs": [{"text": str, "marks": {...}} | {"image": key}]}

Marks are ``bold``, ``italic``, ``underline``, ``super``, ``sub`` (True),
``font`` (family), ``size`` (points) and ``color``/``highlight``
("#rrggbb"). Images are PNG bytes keyed by name. List markers ("• ",
"1. ") are ordinary text at the start of the paragraph, so every format
shows them without list support of its own.

Formats follow GTK3 Write (sugarlabs/write-activity): its export menu offers
RTF, HTML, plain text and PDF, and it saves new documents as RTF.
"""

import base64
import html
import html.parser
import json
import re

FORMAT = "aspartame-write-v2"
STYLES = ("normal", "h1", "h2", "h3", "h4", "block", "plain")
ALIGNS = ("left", "center", "right", "fill")
LISTS = (None, "bullet", "dash", "number", "lower", "upper")
FLAGS = ("bold", "italic", "underline", "super", "sub")
STYLE_SIZES = {"h1": 24, "h2": 20, "h3": 16, "h4": 14}
MARKER = re.compile(r"^(• |– |\d+\. |[a-z]\. |[A-Z]\. )")
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


def paragraph(text="", style="normal", align="left", list_kind=None, marks=None):
    runs = [{"text": text, "marks": dict(marks or {})}] if text else []
    return {"style": style, "align": align, "list": list_kind, "runs": runs}


def marker(list_kind, number):
    if list_kind == "bullet":
        return "• "
    if list_kind == "dash":
        return "– "
    if list_kind == "number":
        return "%d. " % number
    letter = chr(ord("a") + (number - 1) % 26)
    return (letter if list_kind == "lower" else letter.upper()) + ". "


def plain_text(doc):
    return "\n".join("".join(r.get("text", "\ufffc") for r in p["runs"]) for p in doc["paragraphs"])


# Validation

def _check_marks(marks):
    if not isinstance(marks, dict):
        raise ValueError("marks must be an object")
    for key, value in marks.items():
        if key in FLAGS:
            ok = value is True
        elif key == "font":
            ok = isinstance(value, str) and 0 < len(value) < 80
        elif key == "size":
            ok = isinstance(value, int) and not isinstance(value, bool) and 4 <= value <= 144
        elif key in ("color", "highlight"):
            ok = isinstance(value, str) and bool(HEX.match(value))
        else:
            ok = False
        if not ok:
            raise ValueError("bad mark %s=%r" % (key, value))


def validate(doc):
    if not isinstance(doc, dict) or doc.get("format") != FORMAT:
        raise ValueError("not a Write document")
    images = doc.get("images", {})
    if not isinstance(images, dict):
        raise ValueError("images must be an object")
    for key, data in images.items():
        if not isinstance(data, str) or not base64.b64decode(data, validate=True).startswith(b"\x89PNG"):
            raise ValueError("image %r is not a PNG" % key)
    paragraphs = doc.get("paragraphs")
    if not isinstance(paragraphs, list) or not paragraphs:
        raise ValueError("paragraphs must be a non-empty list")
    for p in paragraphs:
        if not isinstance(p, dict) or p.get("style") not in STYLES or p.get("align") not in ALIGNS \
                or p.get("list") not in LISTS or not isinstance(p.get("runs"), list):
            raise ValueError("malformed paragraph")
        for run in p["runs"]:
            if not isinstance(run, dict):
                raise ValueError("malformed run")
            if "image" in run:
                if run["image"] not in images:
                    raise ValueError("missing image %r" % run["image"])
            elif not isinstance(run.get("text"), str) or "\n" in run["text"]:
                raise ValueError("malformed text run")
            else:
                _check_marks(run.get("marks", {}))
    return doc


def new_document():
    return {"format": FORMAT, "paragraphs": [paragraph()], "images": {}}


def from_text(text):
    return {"format": FORMAT, "images": {},
            "paragraphs": [paragraph(line) for line in text.split("\n")]}


def from_v1(payload):
    """GTK4 Write 1: ``{"format": "aspartame-write-v1", "text", "spans"}``."""
    text = payload.get("text")
    spans = payload.get("spans", [])
    if not isinstance(text, str) or not isinstance(spans, list):
        raise ValueError("malformed Write 1 document")
    flags = [set() for _ in text]
    for span in spans:
        try:
            start, end = max(0, int(span["start"])), min(len(text), int(span["end"]))
            tags = span["tags"]
        except (KeyError, TypeError, ValueError):
            raise ValueError("malformed Write 1 span")
        for i in range(start, end):
            flags[i].update(t for t in tags if t in ("bold", "italic", "heading"))
    doc = {"format": FORMAT, "images": {}, "paragraphs": []}
    offset = 0
    for line in text.split("\n"):
        p = paragraph()
        line_flags = flags[offset:offset + len(line)]
        if line and all("heading" in f for f in line_flags):
            p["style"] = "h2"
        for i, ch in enumerate(line):
            marks = {k: True for k in ("bold", "italic") if k in line_flags[i]}
            if p["runs"] and p["runs"][-1].get("marks") == marks:
                p["runs"][-1]["text"] += ch
            else:
                p["runs"].append({"text": ch, "marks": marks})
        doc["paragraphs"].append(p)
        offset += len(line) + 1
    return doc


def loads(raw):
    """Open a Journal payload: a Write document, Write 1 JSON, RTF, HTML or text."""
    if raw.lstrip().startswith("{\\rtf"):
        return read_rtf(raw), "application/rtf"
    if raw.lstrip().startswith("{"):
        try:
            payload = json.loads(raw)
        except ValueError:
            return from_text(raw), "text/plain"
        if isinstance(payload, dict) and payload.get("format") == FORMAT:
            return validate(payload), None
        if isinstance(payload, dict) and payload.get("format") == "aspartame-write-v1":
            return from_v1(payload), None
        raise ValueError("unsupported Write document")
    if re.match(r"\s*(<!DOCTYPE html|<html)", raw, re.I):
        return read_html(raw), "text/html"
    return from_text(raw), "text/plain"


def dumps(doc):
    return json.dumps(validate(doc), ensure_ascii=False, sort_keys=True) + "\n"


# HTML

_HTML_TAG = {"normal": "p", "h1": "h1", "h2": "h2", "h3": "h3", "h4": "h4",
             "block": "blockquote", "plain": "pre"}


def _html_run(run, images):
    if "image" in run:
        return '<img alt="" src="data:image/png;base64,%s">' % images[run["image"]]
    text = html.escape(run["text"])
    marks = run.get("marks", {})
    style = []
    if "font" in marks:
        style.append("font-family: %s" % html.escape(marks["font"]))
    if "size" in marks:
        style.append("font-size: %dpt" % marks["size"])
    if "color" in marks:
        style.append("color: %s" % marks["color"])
    if "highlight" in marks:
        style.append("background-color: %s" % marks["highlight"])
    if style:
        text = '<span style="%s">%s</span>' % ("; ".join(style), text)
    for flag, tag in (("bold", "b"), ("italic", "i"), ("underline", "u"),
                      ("super", "sup"), ("sub", "sub")):
        if marks.get(flag):
            text = "<%s>%s</%s>" % (tag, text, tag)
    return text


def write_html(doc, title="Write document"):
    body = []
    for p in doc["paragraphs"]:
        tag = _HTML_TAG[p["style"]]
        align = ' style="text-align: %s"' % ("justify" if p["align"] == "fill" else p["align"]) \
            if p["align"] != "left" else ""
        content = "".join(_html_run(r, doc["images"]) for r in p["runs"]) or "<br>"
        body.append("<%s%s>%s</%s>" % (tag, align, content, tag))
    return ('<!DOCTYPE html>\n<html><head><meta charset="utf-8"><title>%s</title></head>\n'
            "<body>\n%s\n</body></html>\n" % (html.escape(title), "\n".join(body)))


class _HTMLReader(html.parser.HTMLParser):
    BLOCKS = {"p": "normal", "div": "normal", "li": "normal", "h1": "h1", "h2": "h2", "h3": "h3",
              "h4": "h4", "h5": "h4", "h6": "h4", "blockquote": "block", "pre": "plain"}
    FLAG_TAGS = {"b": "bold", "strong": "bold", "i": "italic", "em": "italic", "u": "underline",
                 "sup": "super", "sub": "sub"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.doc = {"format": FORMAT, "images": {}, "paragraphs": []}
        self.stack = [{}]
        self.current = None
        self.skip = 0

    def _para(self, style="normal", align="left"):
        self.current = paragraph(style=style, align=align)
        self.doc["paragraphs"].append(self.current)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ("script", "style", "head", "title"):
            self.skip += 1
            return
        css = dict(item.split(":", 1) for item in (attrs.get("style") or "").split(";") if ":" in item)
        css = {k.strip().lower(): v.strip() for k, v in css.items()}
        if tag in self.BLOCKS:
            align = {"center": "center", "right": "right", "justify": "fill"}.get(css.get("text-align"), "left")
            self._para(self.BLOCKS[tag], align)
        if tag == "br":
            self._para()
            return
        if tag == "img":
            src = attrs.get("src") or ""
            if src.startswith("data:image/png;base64,"):
                key = "image%d" % (len(self.doc["images"]) + 1)
                self.doc["images"][key] = src.split(",", 1)[1]
                if self.current is None:
                    self._para()
                self.current["runs"].append({"image": key})
            return
        marks = dict(self.stack[-1])
        if tag in self.FLAG_TAGS:
            marks[self.FLAG_TAGS[tag]] = True
        if css.get("font-family"):
            marks["font"] = css["font-family"].split(",")[0].strip("'\" ")
        match = re.match(r"(\d+)pt", css.get("font-size", ""))
        if match:
            marks["size"] = max(4, min(144, int(match.group(1))))
        for prop, key in (("color", "color"), ("background-color", "highlight")):
            if HEX.match(css.get(prop, "")):
                marks[key] = css[prop].lower()
        self.stack.append(marks)

    def handle_endtag(self, tag):
        if tag in ("script", "style", "head", "title"):
            self.skip = max(0, self.skip - 1)
            return
        if tag in ("br", "img"):
            return
        if len(self.stack) > 1:
            self.stack.pop()
        if tag in self.BLOCKS:
            self.current = None

    def handle_data(self, data):
        if self.skip:
            return
        data = re.sub(r"\s+", " ", data)
        if not data.strip() and self.current is None:
            return
        if self.current is None:
            self._para()
        _append(self.current, data, self.stack[-1])


def _append(p, text, marks):
    if not text:
        return
    marks = dict(marks)
    if p["runs"] and "text" in p["runs"][-1] and p["runs"][-1].get("marks", {}) == marks:
        p["runs"][-1]["text"] += text
    else:
        p["runs"].append({"text": text, "marks": marks})


def read_html(raw):
    reader = _HTMLReader()
    reader.feed(raw)
    reader.close()
    doc = reader.doc
    if not doc["paragraphs"]:
        doc["paragraphs"].append(paragraph())
    _merge_runs(doc)
    _detect_lists(doc)
    return validate(doc)


# RTF

def _rtf_text(text):
    out = []
    for ch in text:
        if ch in "\\{}":
            out.append("\\" + ch)
        elif ord(ch) < 128:
            out.append(ch)
        else:
            data = ch.encode("utf-16-le")
            for i in range(0, len(data), 2):
                unit = int.from_bytes(data[i:i + 2], "little")
                out.append("\\u%d?" % (unit - 65536 if unit > 32767 else unit))
    return "".join(out)


def write_rtf(doc):
    fonts, colors = ["Sans", "Monospace"], []
    for p in doc["paragraphs"]:
        for run in p["runs"]:
            marks = run.get("marks", {})
            if marks.get("font") and marks["font"] not in fonts:
                fonts.append(marks["font"])
            for key in ("color", "highlight"):
                if marks.get(key) and marks[key].lower() not in colors:
                    colors.append(marks[key].lower())
    out = ["{\\rtf1\\ansi\\ansicpg1252\\deff0\\uc1",
           "{\\fonttbl%s}" % "".join("{\\f%d %s;}" % (i, f.replace(";", "")) for i, f in enumerate(fonts)),
           "{\\colortbl;%s}" % "".join("\\red%d\\green%d\\blue%d;" % tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))
                                      for c in colors)]
    for p in doc["paragraphs"]:
        size = STYLE_SIZES.get(p["style"], 12)
        head = "\\pard\\q%s" % {"left": "l", "center": "c", "right": "r", "fill": "j"}[p["align"]]
        if p["list"]:
            head += "\\li720"
        if p["style"] == "block":
            head += "\\li720\\ri720"
        head += "{\\*\\aspstyle %s}" % p["style"]
        if p["list"]:
            head += "{\\*\\asplist %s}" % p["list"]
        out.append(head)
        for run in p["runs"]:
            if "image" in run:
                data = base64.b64decode(doc["images"][run["image"]])
                width, height = int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")
                out.append("{\\pict\\pngblip\\picw%d\\pich%d\\picwgoal%d\\pichgoal%d %s}" % (
                    width, height, width * 15, height * 15, data.hex()))
                continue
            marks = run.get("marks", {})
            codes = ["\\plain", "\\f%d" % fonts.index(marks.get("font", "Sans") if marks.get("font") else "Sans"),
                     "\\fs%d" % (2 * marks.get("size", size))]
            if p["style"] == "plain" and "font" not in marks:
                codes[1] = "\\f1"
            if marks.get("bold") or p["style"] in STYLE_SIZES:
                codes.append("\\b")
            for flag, code in (("italic", "\\i"), ("underline", "\\ul"), ("super", "\\super"), ("sub", "\\sub")):
                if marks.get(flag):
                    codes.append(code)
            if marks.get("color"):
                codes.append("\\cf%d" % (colors.index(marks["color"].lower()) + 1))
            if marks.get("highlight"):
                codes.append("\\highlight%d" % (colors.index(marks["highlight"].lower()) + 1))
            out.append("{%s %s}" % ("".join(codes), _rtf_text(run["text"])))
        out.append("\\par")
    out.append("}")
    return "\n".join(out) + "\n"


_RTF_TOKEN = re.compile(r"\\([a-zA-Z]+)(-?\d+)? ?|\\'([0-9a-fA-F]{2})|\\(.)|([{}])|([^\\{}\r\n]+)|[\r\n]+")
_SKIP_DESTINATIONS = {"fonttbl", "colortbl", "stylesheet", "info", "listtable", "listoverridetable",
                      "header", "footer", "footnote", "field", "fldinst", "generator", "rsidtbl",
                      "xmlnstbl", "themedata", "colorschememapping", "latentstyles", "datastore",
                      "revtbl", "pgdsctbl"}


def read_rtf(raw):
    """Read the RTF that GTK3 Write (AbiWord) and this module write.

    Character and paragraph formatting, Unicode and PNG pictures are kept;
    tables become one paragraph per row, other destinations are skipped.
    """
    if not raw.lstrip().startswith("{\\rtf"):
        raise ValueError("not an RTF document")
    fonts, colors = {}, []
    doc = {"format": FORMAT, "images": {}, "paragraphs": [paragraph()]}
    state = {"marks": {}, "skip": False, "dest": None, "uc": 1, "font_id": None}
    stack, pending_skip, para = [], 0, doc["paragraphs"][0]
    pict = None
    for match in _RTF_TOKEN.finditer(raw):
        word, arg, hexchar, symbol, brace, text = match.groups()
        if brace == "{":
            stack.append(dict(state, marks=dict(state["marks"])))
            state["dest"] = "fonttbl" if state["dest"] in ("fonttbl", "fonttbl_entry") else None
            state["star"] = False
            continue
        if brace == "}":
            if pict is not None and state["dest"] == "pict" and pict["png"]:
                key = "image%d" % (len(doc["images"]) + 1)
                try:
                    data = bytes.fromhex(pict["hex"])
                except ValueError:
                    data = b""
                if data.startswith(b"\x89PNG"):
                    doc["images"][key] = base64.b64encode(data).decode()
                    para["runs"].append({"image": key})
                pict = None
            if state["dest"] == "fonttbl_entry" and state["font_id"] is not None:
                fonts[state["font_id"]] = state.get("font_name", "").strip().rstrip(";")
            if not stack:
                break
            state = stack.pop()
            continue
        if state["dest"] == "pict":
            if text:
                pict["hex"] += re.sub(r"\s", "", text)
            elif word == "pngblip":
                pict["png"] = True
            continue
        if state["dest"] == "colortbl":
            if word in ("red", "green", "blue"):
                if state.get("rgb") is None:
                    state["rgb"] = {}
                state["rgb"][word] = int(arg or 0)
            elif text and ";" in text:
                for _ in range(text.count(";")):
                    rgb = state.get("rgb")
                    colors.append("#%02x%02x%02x" % (rgb["red"], rgb["green"], rgb["blue"]) if rgb else None)
                    state["rgb"] = None
            continue
        if state["dest"] in ("fonttbl", "fonttbl_entry"):
            if word == "f":
                state["dest"], state["font_id"] = "fonttbl_entry", int(arg or 0)
                state["font_name"] = ""
            elif text and state["dest"] == "fonttbl_entry":
                state["font_name"] = state.get("font_name", "") + text
            continue
        if state["dest"] == "aspstyle" or state["dest"] == "asplist":
            if text:
                value = text.strip()
                if state["dest"] == "aspstyle" and value in STYLES:
                    para["style"] = value
                elif state["dest"] == "asplist" and value in LISTS:
                    para["list"] = value
            continue
        if state["skip"]:
            continue
        if symbol == "*":
            state["star"] = True   # an optional destination: skip it unless known
            continue
        if state.get("star"):
            state["star"] = False
            if word in ("aspstyle", "asplist"):
                state["dest"] = word
            elif word != "shppict":   # AbiWord wraps pictures in \*\shppict
                state["skip"] = True
            continue
        if word:
            n = int(arg) if arg is not None else None
            if word in ("fonttbl", "colortbl"):
                state["dest"] = word
                if word == "colortbl":
                    state["rgb"] = None
            elif word == "pict":
                state["dest"], pict = "pict", {"hex": "", "png": False}
            elif word in _SKIP_DESTINATIONS or word == "nonshppict":
                state["skip"] = True
            elif word in ("par", "row", "line"):
                para = paragraph()
                doc["paragraphs"].append(para)
            elif word == "cell":
                _append(para, "\t", state["marks"])
            elif word == "pard":
                para.update(style="normal", align="left", list=None)
            elif word in ("ql", "qc", "qr", "qj"):
                para["align"] = {"ql": "left", "qc": "center", "qr": "right", "qj": "fill"}[word]
            elif word == "plain":
                state["marks"] = {}
            elif word in ("b", "i", "ul", "super", "sub"):
                flag = {"b": "bold", "i": "italic", "ul": "underline"}.get(word, word)
                if n == 0:
                    state["marks"].pop(flag, None)
                else:
                    state["marks"][flag] = True
            elif word in ("ulnone", "nosupersub"):
                for flag in (("underline",) if word == "ulnone" else ("super", "sub")):
                    state["marks"].pop(flag, None)
            elif word == "fs" and n:
                state["marks"]["size"] = max(4, min(144, n // 2))
            elif word == "f" and n is not None and fonts.get(n):
                state["marks"]["font"] = fonts[n]
            elif word in ("cf", "highlight", "cb") and n is not None:
                key = "color" if word == "cf" else "highlight"
                if 0 < n < len(colors) and colors[n]:
                    state["marks"][key] = colors[n]
                else:
                    state["marks"].pop(key, None)
            elif word == "uc" and n is not None:
                state["uc"] = n
            elif word == "u" and n is not None:
                _append(para, chr(n + 65536 if n < 0 else n), state["marks"])
                pending_skip = state["uc"]
            elif word == "tab":
                _append(para, "\t", state["marks"])
            elif word in ("emdash", "endash", "bullet", "lquote", "rquote", "ldblquote", "rdblquote"):
                _append(para, {"emdash": "—", "endash": "–", "bullet": "•", "lquote": "‘",
                               "rquote": "’", "ldblquote": "“", "rdblquote": "”"}[word], state["marks"])
            continue
        if hexchar:
            if pending_skip:
                pending_skip -= 1
                continue
            _append(para, bytes([int(hexchar, 16)]).decode("cp1252", "replace"), state["marks"])
            continue
        if symbol:
            if pending_skip:
                pending_skip -= 1
                continue
            if symbol in "\\{}":
                _append(para, symbol, state["marks"])
            elif symbol == "~":
                _append(para, "\u00a0", state["marks"])
            continue
        if text:
            if pending_skip:
                drop = min(pending_skip, len(text))
                text, pending_skip = text[drop:], pending_skip - drop
            _append(para, text, state["marks"])
    # The writer ends every paragraph with \par; drop the empty tail.
    if len(doc["paragraphs"]) > 1 and not doc["paragraphs"][-1]["runs"]:
        doc["paragraphs"].pop()
    for p in doc["paragraphs"]:
        size = STYLE_SIZES.get(p["style"])
        for run in p["runs"]:
            marks = run.get("marks", {})
            if size and marks.get("size") == size:
                marks.pop("size")
            if p["style"] in STYLE_SIZES:
                marks.pop("bold", None)
            if p["style"] == "plain" and marks.get("font") == "Monospace":
                marks.pop("font")
            if marks.get("size") == 12 and p["style"] not in STYLE_SIZES:
                marks.pop("size")
            if marks.get("font") == "Sans":
                marks.pop("font")
    _merge_runs(doc)
    _detect_lists(doc)
    return validate(doc)


def list_kind_of(text):
    """The list type a paragraph's leading marker implies, if any."""
    match = MARKER.match(text)
    if not match:
        return None
    mark = match.group(1)
    return {"• ": "bullet", "– ": "dash"}.get(
        mark, "number" if mark[0].isdigit() else ("lower" if mark[0].islower() else "upper"))


def _detect_lists(doc):
    for p in doc["paragraphs"]:
        if p["runs"] and "text" in p["runs"][0]:
            # AbiWord writes list markers as "{\listtext 1.\tab}".
            p["runs"][0]["text"] = re.sub(r"^(•|–|\d+\.|[a-zA-Z]\.)\t", r"\1 ", p["runs"][0]["text"])
        if not p["list"] and p["runs"] and "text" in p["runs"][0]:
            p["list"] = list_kind_of(p["runs"][0]["text"])


def _merge_runs(doc):
    for p in doc["paragraphs"]:
        merged = []
        for run in p["runs"]:
            if "text" in run and not run["text"]:
                continue
            if merged and "text" in run and "text" in merged[-1] and \
                    merged[-1].get("marks", {}) == run.get("marks", {}):
                merged[-1]["text"] += run["text"]
            else:
                merged.append(run)
        p["runs"] = merged


def write_txt(doc):
    return plain_text(doc).replace("\ufffc", "") + "\n"


EXPORTS = {
    "rtf": ("Rich Text (RTF)", "application/rtf", ".rtf"),
    "html": ("Hypertext (HTML)", "text/html", ".html"),
    "txt": ("Plain Text (TXT)", "text/plain", ".txt"),
    "pdf": ("Portable Document Format (PDF)", "application/pdf", ".pdf"),
}
SAVE_AS = {"application/rtf": write_rtf, "text/rtf": write_rtf, "text/html": write_html,
           "text/plain": write_txt}
