"""Format, save, resume, undo and find in GTK4 Write.  Prints write-formatting=PASS."""

import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parents[1] / "packages/gtk4-write-activity")]

import gi  # noqa: E402

gi.require_version("Gtk", "4.0")
import writeactivity4 as write  # noqa: E402


def main():
    tmp = Path(tempfile.mkdtemp())
    activity = write.WriteActivity(None)
    buffer = activity.buffer
    buffer.set_text("Title\nhello <b>world</b> & more\n\nend")
    found = buffer.get_iter_at_line(0)
    buffer.place_cursor(found[1] if isinstance(found, tuple) else found)
    activity.block_choice.set_selected(1)
    activity.align_choice.set_selected(1)
    buffer.select_range(buffer.get_iter_at_offset(12), buffer.get_iter_at_offset(17))
    activity.inline_buttons["bold"].set_active(True)

    saved = tmp / "doc"
    activity.write_file(str(saved))
    text = saved.read_text()
    assert text.startswith("<!DOCTYPE html>\n" + write.FORMAT_MARKER)
    assert '<h1 style="text-align:center">Title</h1>' in text
    assert "&lt;b&gt;" in text and "&amp;" in text and "<b>" in text
    assert activity.metadata["mime_type"] == "text/html"

    resumed = write.WriteActivity(None)
    resumed.read_file(str(saved))
    assert resumed._text() == "Title\nhello <b>world</b> & more\n\nend"
    again = tmp / "again"
    resumed.write_file(str(again))
    assert again.read_text() == text

    plain = write.WriteActivity(None)
    plain.buffer.set_text("<!DOCTYPE html> is just text here")
    plain.write_file(str(tmp / "plain"))
    assert (tmp / "plain").read_text() == "<!DOCTYPE html> is just text here"
    plain.read_file(str(tmp / "plain"))
    assert plain._text() == "<!DOCTYPE html> is just text here"

    resumed._clear()
    assert resumed._text() == ""
    resumed._undo()
    assert resumed._text().startswith("Title")
    resumed.find_entry.set_text("WORLD")
    resumed._find(True)
    assert resumed.status.get_text() == "Found “WORLD”"
    print("write-formatting=PASS")


if __name__ == "__main__":
    main()
