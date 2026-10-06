from pathlib import Path


ROOT = Path(__file__).parents[1]
PACKAGE_ROOT = ROOT / "packages"


def test_native_gtk4_activities_do_not_reintroduce_collapsed_paned_layouts():
    offenders = []
    for source in sorted(PACKAGE_ROOT.glob("gtk4-*/*.py")):
        text = source.read_text(errors="replace")
        if "Gtk.Paned" in text and "set_position(-1)" in text:
            offenders.append(str(source.relative_to(ROOT)))
    assert offenders == []


def test_compound_activity_surfaces_use_expanding_columns():
    for package in (
        "gtk4-get-books-activity",
        "gtk4-jukebox-activity",
        "gtk4-markdown-activity",
        "gtk4-pippy-activity",
    ):
        sources = list((PACKAGE_ROOT / package).glob("*.py"))
        source = "\n".join(path.read_text() for path in sources)
        if "Gtk.Paned" in source:
            assert "set_start_child(" in source
            assert "set_end_child(" in source
            assert "set_position(" in source
            assert "set_position(-1)" not in source
        else:
            assert "Gtk.Grid" in source
            assert "set_column_homogeneous(True)" in source
