"""Small, offline GTK4 Python playground for Sugar."""

import subprocess
import sys
import threading
from pathlib import Path

from gi.repository import Gdk, GLib, Gtk
from sugar4.activity import SimpleActivity


DEFAULT_PROGRAM = '''print("Hello from Pippy!")
for number in range(1, 4):
    print("Python number", number)
'''


class PippyActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Pippy")
        self._build()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        root.set_margin_top(24)
        root.set_margin_bottom(24)
        root.set_margin_start(30)
        root.set_margin_end(30)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Pippy Python playground"])

        title = Gtk.Label(label="Pippy", xalign=0)
        title.add_css_class("title-1")
        root.append(title)
        subtitle = Gtk.Label(label="Write a small Python program, then run it safely offline.", xalign=0)
        subtitle.add_css_class("dim-label")
        root.append(subtitle)

        self.editor = Gtk.TextView()
        self.editor.set_monospace(True)
        self.editor.set_wrap_mode(Gtk.WrapMode.NONE)
        self.editor.set_vexpand(True)
        self.editor.update_property([Gtk.AccessibleProperty.LABEL], ["Python program editor"])
        self.editor.get_buffer().set_text(DEFAULT_PROGRAM)
        editor_scroll = Gtk.ScrolledWindow()
        editor_scroll.set_min_content_height(260)
        editor_scroll.set_vexpand(True)
        editor_scroll.set_child(self.editor)
        root.append(editor_scroll)

        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        run = Gtk.Button(label="Run")
        run.add_css_class("suggested-action")
        run.connect("clicked", self._run_program)
        controls.append(run)
        reset = Gtk.Button(label="Reset example")
        reset.connect("clicked", self._reset)
        controls.append(reset)
        root.append(controls)

        self.output = Gtk.TextView()
        self.output.set_editable(False)
        self.output.set_cursor_visible(False)
        self.output.set_monospace(True)
        self.output.update_property([Gtk.AccessibleProperty.LABEL], ["Program output"])
        output_scroll = Gtk.ScrolledWindow()
        output_scroll.set_min_content_height(130)
        output_scroll.set_child(self.output)
        root.append(output_scroll)
        self.status = Gtk.Label(label="Ready", xalign=0)
        self.status.add_css_class("dim-label")
        root.append(self.status)
        self.set_canvas(root)

        provider = Gtk.CssProvider()
        provider.load_from_data(b"textview { padding: 10px; } button { min-height: 42px; border-radius: 19px; }")
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _program(self):
        start, end = self.editor.get_buffer().get_bounds()
        return self.editor.get_buffer().get_text(start, end, False)

    def _run_program(self, _button):
        self.status.set_text("Running…")
        threading.Thread(target=self._execute, args=(self._program(),), daemon=True).start()

    def _execute(self, program):
        try:
            result = subprocess.run([sys.executable, "-I", "-c", program], capture_output=True,
                                    text=True, timeout=5, check=False)
            text = result.stdout
            if result.stderr:
                text += ("\n" if text else "") + result.stderr
            GLib.idle_add(self._show_result, text or "(program finished without output)", result.returncode)
        except (subprocess.TimeoutExpired, OSError) as error:
            GLib.idle_add(self._show_result, str(error), 1)

    def _show_result(self, text, returncode):
        self.output.get_buffer().set_text(text)
        self.status.set_text("Finished" if returncode == 0 else "Program returned an error")
        return GLib.SOURCE_REMOVE

    def _reset(self, _button):
        self.editor.get_buffer().set_text(DEFAULT_PROGRAM)
        self.output.get_buffer().set_text("")
        self.status.set_text("Ready")

    def read_file(self, file_path):
        """Restore a Python source buffer from a UTF-8 Journal object."""
        try:
            program = Path(file_path).read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            program = DEFAULT_PROGRAM
        self.editor.get_buffer().set_text(program)
        self.output.get_buffer().set_text("")
        self.status.set_text("Ready")

    def write_file(self, file_path):
        """Save the Python source buffer as a UTF-8 Journal object."""
        Path(file_path).write_text(self._program(), encoding="utf-8")
