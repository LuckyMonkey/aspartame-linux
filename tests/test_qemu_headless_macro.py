from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_headless_macro_uses_qmp_without_x11_window_automation():
    script = (ROOT / "scripts/qemu-headless-macro.py").read_text()
    assert '"human-monitor-command"' in script
    assert '"sendkey' in script
    assert '"screendump"' in script
    assert "xdotool" not in script
    assert "windowactivate" not in script


def test_headless_macro_supports_absolute_tablet_clicks_and_text():
    script = (ROOT / "scripts/qemu-headless-macro.py").read_text()
    assert '"type": "abs"' in script
    assert '"type": "btn"' in script
    assert "release: dict[str, Any]" in script
    assert 'self.command("input-send-event", release)' in script
    assert "def text_keys" in script
    assert "32767 / SCREEN_WIDTH" in script
