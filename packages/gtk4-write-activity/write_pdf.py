"""PDF export for Write documents through Pango and cairo (no GTK widgets)."""

import base64
import io

import cairo
import gi

gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import GLib, Pango, PangoCairo  # noqa: E402

from write_doc import STYLE_SIZES  # noqa: E402

PAGE_W, PAGE_H, MARGIN = 595, 842, 56   # A4 in points


def _markup(runs, style):
    parts = []
    for run in runs:
        marks = run.get("marks", {})
        attrs = []
        if marks.get("font") or style == "plain":
            attrs.append('font_family="%s"' % GLib.markup_escape_text(marks.get("font", "Monospace")))
        size = marks.get("size") or STYLE_SIZES.get(style)
        if size:
            attrs.append('size="%d"' % (size * Pango.SCALE))
        if marks.get("bold") or style in STYLE_SIZES:
            attrs.append('weight="bold"')
        if marks.get("italic"):
            attrs.append('style="italic"')
        if marks.get("underline"):
            attrs.append('underline="single"')
        if marks.get("color"):
            attrs.append('foreground="%s"' % marks["color"])
        if marks.get("highlight"):
            attrs.append('background="%s"' % marks["highlight"])
        text = GLib.markup_escape_text(run["text"])
        if marks.get("super"):
            text = "<sup>%s</sup>" % text
        elif marks.get("sub"):
            text = "<sub>%s</sub>" % text
        parts.append("<span %s>%s</span>" % (" ".join(attrs), text) if attrs else text)
    return "".join(parts)


class _Pages:
    def __init__(self, path):
        self.surface = cairo.PDFSurface(str(path), PAGE_W, PAGE_H)
        self.cr = cairo.Context(self.surface)
        self.y = MARGIN
        self.count = 1

    def need(self, height):
        if self.y + height > PAGE_H - MARGIN and self.y > MARGIN:
            self.cr.show_page()
            self.y = MARGIN
            self.count += 1


def write_pdf(doc, path):
    """Render ``doc`` to an A4 PDF at ``path``; returns the page count."""
    pages = _Pages(path)
    cr = pages.cr
    width = PAGE_W - 2 * MARGIN
    for p in doc["paragraphs"]:
        indent = 36 if p["style"] == "block" else (18 if p["list"] else 0)
        segments, text_runs = [], []
        for run in p["runs"]:
            if "image" in run:
                segments.append(("text", text_runs))
                segments.append(("image", run["image"]))
                text_runs = []
            else:
                text_runs.append(run)
        segments.append(("text", text_runs))
        for kind, value in segments:
            if kind == "image":
                image = cairo.ImageSurface.create_from_png(io.BytesIO(base64.b64decode(doc["images"][value])))
                scale = min(1.0, (width - indent) / image.get_width())
                height = image.get_height() * scale
                pages.need(height)
                cr.save()
                cr.translate(MARGIN + indent, pages.y)
                cr.scale(scale, scale)
                cr.set_source_surface(image, 0, 0)
                cr.paint()
                cr.restore()
                pages.y += height + 4
                continue
            if not value and any(k == "image" for k, _v in segments):
                continue
            layout = PangoCairo.create_layout(cr)
            layout.set_width(int((width - 2 * indent if p["style"] == "block" else width - indent) * Pango.SCALE))
            layout.set_wrap(Pango.WrapMode.WORD_CHAR)
            layout.set_font_description(Pango.FontDescription.from_string("Sans 12"))
            layout.set_alignment({"left": Pango.Alignment.LEFT, "center": Pango.Alignment.CENTER,
                                  "right": Pango.Alignment.RIGHT, "fill": Pango.Alignment.LEFT}[p["align"]])
            layout.set_justify(p["align"] == "fill")
            layout.set_markup(_markup(value, p["style"]) or " ", -1)
            iterator = layout.get_iter()
            while True:
                line = iterator.get_line_readonly()
                _ink, logical = iterator.get_line_extents()
                height = logical.height / Pango.SCALE
                pages.need(height)
                baseline = (iterator.get_baseline() - logical.y) / Pango.SCALE
                cr.set_source_rgb(0, 0, 0)
                cr.move_to(MARGIN + indent + logical.x / Pango.SCALE, pages.y + baseline)
                PangoCairo.show_layout_line(cr, line)
                pages.y += height
                if not iterator.next_line():
                    break
        pages.y += 6
    pages.surface.finish()
    return pages.count
