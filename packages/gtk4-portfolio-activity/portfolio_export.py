"""Dependency-free HTML export for the GTK4 Portfolio activity."""

from html import escape
from pathlib import Path


def render_html(title, body):
    """Render a small safe HTML document from a portfolio title and body."""
    safe_title = escape(str(title).strip() or "Untitled project")
    paragraphs = str(body).split("\n\n")
    content = "\n".join(
        "<p>%s</p>" % escape(paragraph).replace("\n", "<br>\n")
        for paragraph in paragraphs
        if paragraph.strip()
    ) or "<p></p>"
    return (
        "<!doctype html>\n"
        '<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "<title>%s</title>\n"
        "<style>body{font:16px sans-serif;line-height:1.55;max-width:48rem;"
        "margin:2rem auto;padding:0 1rem;color:#20252a}h1{line-height:1.2}"
        "</style>\n</head>\n<body>\n<h1>%s</h1>\n%s\n</body>\n</html>\n"
        % (safe_title, safe_title, content)
    )


def write_html(path, title, body):
    Path(path).write_text(render_html(title, body), encoding="utf-8")
