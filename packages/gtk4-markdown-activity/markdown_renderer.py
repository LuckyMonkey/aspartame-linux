"""Small, dependency-free Markdown-to-Pango renderer for the GTK4 preview."""

from __future__ import annotations

import html
import re


_HEADING = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$")
_BULLET = re.compile(r"^\s*[-*+]\s+(.+)$")
_ORDERED = re.compile(r"^\s*\d+[.)]\s+(.+)$")
_RULE = re.compile(r"^\s*(?:\*\s*){3,}$|^\s*(?:-\s*){3,}$|^\s*(?:_\s*){3,}$")


def _inline_markup(text: str) -> str:
    """Escape input first, then add only the Pango tags we own."""
    value = html.escape(text, quote=False)
    value = re.sub(r"`([^`\n]+)`", r"<tt>\1</tt>", value)
    value = re.sub(r"\*\*([^*\n]+)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"__([^_\n]+)__", r"<b>\1</b>", value)
    value = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<i>\1</i>", value)
    value = re.sub(r"(?<!_)_([^_\n]+)_(?!_)", r"<i>\1</i>", value)
    value = re.sub(
        r"\[([^]\n]+)\]\(([^)\n]+)\)",
        r'\1 <span foreground="#52636b">(\2)</span>',
        value,
    )
    return value


def render_markdown(source: str) -> str:
    """Render common teaching-document Markdown as safe Pango markup.

    This intentionally does not claim to be a complete CommonMark parser. It
    gives the GTK4 Activity a useful, readable preview without pulling a web
    runtime or allowing source HTML to become widget markup.
    """
    lines: list[str] = []
    fenced = False
    for raw_line in source.splitlines():
        line = raw_line.rstrip()
        if line.strip().startswith("```"):
            if fenced:
                lines.append("</tt>")
            else:
                lines.append("<tt>")
            fenced = not fenced
            continue
        if fenced:
            lines.append(html.escape(line, quote=False))
            continue
        if not line.strip():
            lines.append("")
            continue
        heading = _HEADING.match(line)
        if heading:
            level = len(heading.group(1))
            size = "xx-large" if level == 1 else "x-large" if level == 2 else "large"
            lines.append(
                f'<span size="{size}" weight="bold">'
                f"{_inline_markup(heading.group(2))}</span>"
            )
            continue
        bullet = _BULLET.match(line)
        if bullet:
            lines.append(f"• {_inline_markup(bullet.group(1))}")
            continue
        ordered = _ORDERED.match(line)
        if ordered:
            number = line.lstrip().split(".", 1)[0].split(")", 1)[0]
            lines.append(f"{number}. {_inline_markup(ordered.group(1))}")
            continue
        if line.lstrip().startswith(">"):
            quote = line.lstrip()[1:].lstrip()
            lines.append(
                f'<span style="italic" foreground="#52636b">'
                f"▌ {_inline_markup(quote)}</span>"
            )
            continue
        if _RULE.match(line):
            lines.append('<span foreground="#8aa8b8">────────</span>')
            continue
        lines.append(_inline_markup(line))
    if fenced:
        lines.append("</tt>")
    return "\n".join(lines).strip() or "Start writing with Markdown."
