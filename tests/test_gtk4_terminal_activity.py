from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_build_stages_pinned_gtk4_terminal_activity():
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    init = (ROOT / "scripts/sugar-gtk4-init.sh").read_text()
    assert 'terminal_activity="$root/sources/terminal-activity"' in build
    assert 'ln -sfn "$terminal_activity" "$activity_dir/Terminal.activity"' in build
    assert "terminal-activity|https://github.com/Inuth0603/terminal-activity" in init
