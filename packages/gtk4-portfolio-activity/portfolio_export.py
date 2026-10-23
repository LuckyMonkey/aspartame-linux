"""PDF export for a Portfolio show (cairo and Pango; no GTK widgets).

Like GTK3 Portfolio's exportpdf.py: a cover page with the portfolio title,
date and introduction, then one page per slide with its title, picture
and description.
"""

import io
import time

import cairo
import gi

gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import GdkPixbuf, Pango, PangoCairo  # noqa: E402

PAGE_W, PAGE_H, MARGIN = 504, 648, 36    # GTK3 Portfolio's page size


def _text(cr, text, size, y, bold=False, width=PAGE_W - 2 * MARGIN):
    layout = PangoCairo.create_layout(cr)
    font = Pango.FontDescription.from_string("Sans %s%d" % ("Bold " if bold else "", size))
    layout.set_font_description(font)
    layout.set_width(int(width * Pango.SCALE))
    layout.set_wrap(Pango.WrapMode.WORD_CHAR)
    layout.set_text(text, -1)
    cr.move_to(MARGIN, y)
    PangoCairo.show_layout(cr, layout)
    return y + layout.get_pixel_size()[1]


def _picture(cr, data, y, max_h):
    """Draw image bytes scaled into the page width; returns the new y."""
    if not data:
        return y
    try:
        loader = GdkPixbuf.PixbufLoader()
        loader.write(data)
        loader.close()
        pixbuf = loader.get_pixbuf()
        ok, png = pixbuf.save_to_bufferv("png", [], [])
        image = cairo.ImageSurface.create_from_png(io.BytesIO(bytes(png)))
    except Exception:
        return y
    scale = min((PAGE_W - 2 * MARGIN) / image.get_width(), max_h / image.get_height())
    cr.save()
    cr.translate(MARGIN + (PAGE_W - 2 * MARGIN - image.get_width() * scale) / 2, y)
    cr.scale(scale, scale)
    cr.set_source_surface(image, 0, 0)
    cr.paint()
    cr.restore()
    return y + image.get_height() * scale


def write_pdf(path, title, introduction, slides, pictures, author=""):
    """``pictures`` maps a slide uid to image bytes (file or preview)."""
    surface = cairo.PDFSurface(str(path), PAGE_W, PAGE_H)
    cr = cairo.Context(surface)
    cr.set_source_rgb(0, 0, 0)
    y = _text(cr, title or "Portfolio", 24, MARGIN, bold=True)
    y = _text(cr, " · ".join(p for p in (author, time.strftime("%x")) if p), 12, y + 12)
    if introduction:
        _text(cr, introduction, 12, y + 18)
    cr.show_page()
    for slide in slides:
        y = _text(cr, slide.title or "Untitled", 20, MARGIN, bold=True)
        y = _picture(cr, pictures.get(slide.uid, b""), y + 12, PAGE_H * 0.5)
        if slide.description:
            _text(cr, slide.description, 12, y + 14)
        cr.show_page()
    surface.finish()
    return len(slides) + 1
