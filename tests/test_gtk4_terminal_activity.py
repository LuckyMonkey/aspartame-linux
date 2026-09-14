from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_build_stages_pinned_gtk4_terminal_activity():
    build = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
    init = (ROOT / "scripts/sugar-gtk4-init.sh").read_text()
    assert 'terminal_activity="$root/sources/terminal-activity"' in build
    assert 'ln -sfn "$terminal_activity" "$activity_dir/Terminal.activity"' in build
    assert "terminal-activity|https://github.com/Inuth0603/terminal-activity" in init
    patch = (ROOT / "patches/gtk4-preview/0124-terminal-vte-compat.patch").read_text()
    assert "gi.require_version('Vte', '2.91')" in patch
    assert "*0124*) target=\"$terminal_activity\"" in build
    assert "*0125*) target=\"$terminal_activity\"" in build
