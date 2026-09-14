from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_markdown_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-markdown-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "markdownactivity4.py").read_text()
    assert "bundle_id = org.sugarlabs.Markdown" in info
    assert "sugar-activity4 markdownactivity4.MarkdownActivity" in info
    assert "class MarkdownActivity(SimpleActivity)" in source
    assert "Markdown preview" in source
    assert "org.sugarlabs.Markdown" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-markdown-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-markdown-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
