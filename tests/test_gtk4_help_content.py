from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "packages/gtk4-help-activity/helpactivity4.py"


def test_help_is_english_dark_and_structured():
    source = SOURCE.read_text()
    for heading in (
        "The Sugar shell",
        "Your XO identity",
        "Saving and resuming",
        "Classic and modern Spaces",
        "When an Activity will not open",
    ):
        assert f'("{heading}"' in source
    assert "Gtk.Expander" in source
    assert "GLib.idle_add(expanders[0][0].set_expanded, True)" in source
    assert ".help-root" in source
    assert "#111111" in source
    assert "Search help" in source
    # The modern Help implementation must not regress to the old translated page.
    assert "Bienvenido" not in source
    assert "Contenidos" not in source
