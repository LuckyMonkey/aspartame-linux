from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_qemu_macro_is_a_shell_free_reusable_x11_driver():
    script = (ROOT / "scripts/qemu-macro.py").read_text()
    assert '"xdotool", "search"' in script
    assert '"xdotool", "windowmap"' in script
    assert 'subprocess.run(args' in script
    assert "shell=True" not in script
    assert 'ACTION_NAMES = {"activate", "click", "key", "move", "sleep", "screenshot", "text"}' in script


def test_qemu_macro_captures_a_window_and_supports_repeatable_sequences():
    script = (ROOT / "scripts/qemu-macro.py").read_text()
    assert 'run("import", "-window", window, str(output))' in script
    assert 'parser.add_argument("--repeat"' in script
    assert '"--clearmodifiers"' in script
