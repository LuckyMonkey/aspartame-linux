from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_typingturtle_bundle_is_native_and_registered():
    package = ROOT / "packages/gtk4-typingturtle-activity"
    info = (package / "activity/activity.info").read_text()
    source = (package / "typingturtleactivity4.py").read_text()
    assert "bundle_id = org.laptop.community.TypingTurtle" in info
    assert "sugar-activity4 typingturtleactivity4.TypingTurtleActivity" in info
    assert "class TypingTurtleActivity(SimpleActivity)" in source
    assert "Next word" in source
    assert "org.laptop.community.TypingTurtle" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-typingturtle-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-typingturtle-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
