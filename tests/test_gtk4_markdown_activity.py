from pathlib import Path
import sys

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "packages/gtk4-markdown-activity"))
from markdown_renderer import render_markdown


def test_markdown_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-markdown-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "markdownactivity4.py").read_text()
    assert "bundle_id = org.sugarlabs.Markdown" in info
    assert "sugar-activity4 markdownactivity4.MarkdownActivity" in info
    assert "class MarkdownActivity(SimpleActivity)" in source
    assert "Markdown preview" in source
    assert "DEFAULT_MARKDOWN" in source and "Start writing here" in source
    assert "self.editor.get_buffer().set_text(DEFAULT_MARKDOWN)" in source
    assert "editor_frame" in source and "preview_frame" in source
    assert "editor_empty" in source and "Empty Markdown editor" in source
    assert "Markdown source" in source and "Ready · 0 characters" in source
    assert "self.preview.set_yalign(0.0)" in source
    assert "label.markdown-title" in source
    assert "Gtk.Grid" in source and "set_column_homogeneous(True)" in source
    assert "frame.editor-pane" in source
    assert "Gtk.ScrolledWindow" in source
    assert "from markdown_renderer import render_markdown" in source
    assert "org.sugarlabs.Markdown" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-markdown-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-markdown-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()


def test_markdown_journal_roundtrip_is_utf8():
    source = (ROOT / "packages/gtk4-markdown-activity/markdownactivity4.py").read_text()
    assert "def read_file(self, file_path)" in source
    assert "def write_file(self, file_path)" in source
    assert 'encoding="utf-8"' in source


def test_markdown_preview_renders_common_syntax_as_safe_pango_markup():
    rendered = render_markdown(
        "# Title\n\n**bold** *italic* `code` [docs](https://example.test)\n"
        "\n- one\n- two\n\n> note\n\n2 < 3"
    )
    assert '<span size="xx-large" weight="bold">Title</span>' in rendered
    assert "<b>bold</b>" in rendered
    assert "<i>italic</i>" in rendered
    assert "<tt>code</tt>" in rendered
    assert "• one" in rendered
    assert "▌ note" in rendered
    assert "2 &lt; 3" in rendered
    assert "<script" not in rendered
