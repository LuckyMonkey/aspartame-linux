"""Small, offline GTK4 Python playground for Sugar.

The editor keeps useful teaching affordances—examples, program input,
Python indentation, Ctrl+Enter execution, and traceback line navigation—
while execution remains inside the bounded local runner.
"""

import re
import threading
from pathlib import Path

from gi.repository import Gdk, GLib, Gtk
from sugar4.activity import SimpleActivity
from pippy_runner import run_program, runtime_descriptor


DEFAULT_PROGRAM = '''print("Hello from Pippy!")
for number in range(1, 4):
    print("Python number", number)
'''
OUTPUT_PLACEHOLDER = "Run the program to see output."
EXAMPLES = {
    "Hello": DEFAULT_PROGRAM,
    "Times table": '''number = 7
for row in range(1, 11):
    print(number, "x", row, "=", number * row)
''',
    "Fibonacci": '''a, b = 0, 1
while a < 1000:
    print(a)
    a, b = b, a + b
''',
    "Text art": '''for size in range(1, 8):
    print(" " * (8 - size) + "*" * (2 * size - 1))
print(" " * 7 + "|")
''',
}


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
        root.set_hexpand(True)
        root.set_vexpand(True)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Pippy Python playground"])

        title = Gtk.Label(label="Pippy", xalign=0)
        title.add_css_class("title-1")
        root.append(title)
        subtitle = Gtk.Label(label="Write a small Python program, then run it in a bounded local runner. Use Ctrl+Enter to run.", xalign=0)
        subtitle.add_css_class("dim-label")
        root.append(subtitle)
        runtime = runtime_descriptor()
        runtime_label = Gtk.Label(
            label=(
                f"Runtime: Python {runtime['version']} {runtime['implementation']} · "
                "isolated child · temporary workspace · user site disabled · "
                "network not sandboxed"
            ),
            xalign=0,
        )
        runtime_label.add_css_class("caption")
        runtime_label.add_css_class("dim-label")
        runtime_label.set_wrap(True)
        runtime_label.update_property(
            [Gtk.AccessibleProperty.LABEL], ["Pippy runtime boundary"]
        )
        root.append(runtime_label)

        self.editor = Gtk.TextView()
        self.editor.set_monospace(True)
        self.editor.set_wrap_mode(Gtk.WrapMode.NONE)
        self.editor.set_vexpand(True)
        self.editor.update_property([Gtk.AccessibleProperty.LABEL], ["Python program editor"])
        self.editor.get_buffer().set_text(DEFAULT_PROGRAM)
        keys = Gtk.EventControllerKey()
        keys.connect("key-pressed", self._editor_key)
        self.editor.add_controller(keys)
        editor_scroll = Gtk.ScrolledWindow()
        editor_scroll.set_min_content_height(260)
        editor_scroll.set_hexpand(True)
        editor_scroll.set_vexpand(True)
        editor_scroll.set_child(self.editor)
        editor_frame = Gtk.Frame(label="Python program")
        editor_frame.add_css_class("code-pane")
        editor_frame.set_hexpand(True)
        editor_frame.set_vexpand(True)
        editor_frame.set_child(editor_scroll)

        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        run = Gtk.Button(label="Run")
        run.add_css_class("suggested-action")
        run.update_property([Gtk.AccessibleProperty.LABEL], ["Run Python program"])
        run.connect("clicked", self._run_program)
        controls.append(run)
        stop = Gtk.Button(label="Stop")
        stop.set_sensitive(False)
        stop.update_property([Gtk.AccessibleProperty.LABEL], ["Stop Python program"])
        stop.connect("clicked", self._stop_program)
        controls.append(stop)
        self.examples = Gtk.DropDown.new_from_strings(list(EXAMPLES))
        self.examples.set_tooltip_text("Choose an example program")
        self.examples.update_property([Gtk.AccessibleProperty.LABEL], ["Example programs"])
        controls.append(self.examples)
        reset = Gtk.Button(label="Reset example")
        reset.set_tooltip_text("Replace the program with the selected example")
        reset.update_property([Gtk.AccessibleProperty.LABEL], ["Reset Python example"])
        reset.connect("clicked", self._reset)
        controls.append(reset)
        controls.set_halign(Gtk.Align.END)

        editor_column = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        editor_column.set_hexpand(True); editor_column.set_vexpand(True)
        editor_column.append(editor_frame); editor_column.append(controls)

        self.stdin = Gtk.Entry()
        self.stdin.set_placeholder_text("Program input (separate lines with ;)")
        self.stdin.update_property([Gtk.AccessibleProperty.LABEL], ["Program input"])
        editor_column.append(self.stdin)

        self.output = Gtk.TextView()
        self.output.set_editable(False)
        self.output.set_cursor_visible(False)
        self.output.set_monospace(True)
        self.output.update_property([Gtk.AccessibleProperty.LABEL], ["Program output"])
        output_scroll = Gtk.ScrolledWindow()
        output_scroll.set_min_content_height(130)
        output_scroll.set_hexpand(True)
        output_scroll.set_child(self.output)
        output_frame = Gtk.Frame(label="Output")
        output_frame.add_css_class("code-pane")
        output_frame.set_hexpand(True)
        output_frame.set_vexpand(True)
        output_frame.set_child(output_scroll)

        panes = Gtk.Grid(column_spacing=16)
        panes.set_hexpand(True); panes.set_vexpand(True)
        panes.set_column_homogeneous(True)
        panes.attach(editor_column, 0, 0, 1, 1)
        panes.attach(output_frame, 1, 0, 1, 1)
        root.append(panes)
        self.status = Gtk.Label(label="Ready", xalign=0)
        self.status.add_css_class("dim-label")
        root.append(self.status)
        self.run_button = run
        self.stop_button = stop
        self._run_generation = 0
        self._cancel_event = None
        self.set_canvas(root)
        self.output.get_buffer().set_text(OUTPUT_PLACEHOLDER)

        provider = Gtk.CssProvider()
        provider.load_from_data(b"frame.code-pane { border: 1px solid #8aa8b8; border-radius: 10px; } textview { padding: 10px; } button { min-height: 42px; border-radius: 19px; }")
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _program(self):
        start, end = self.editor.get_buffer().get_bounds()
        return self.editor.get_buffer().get_text(start, end, False)

    def _run_program(self, _button):
        self._run_generation += 1
        generation = self._run_generation
        self.run_button.set_sensitive(False)
        self.stop_button.set_sensitive(True)
        self.status.set_text("Running…")
        self._cancel_event = threading.Event()
        threading.Thread(
            target=self._execute,
            args=(self._program(), self._input_text(), generation, self._cancel_event),
            daemon=True,
        ).start()

    def _input_text(self):
        return "\n".join(part.strip() for part in self.stdin.get_text().split(";")) + "\n"

    def _execute(self, program, input_text, generation, cancel_event):
        try:
            result = run_program(
                program, input_text=input_text, cancel_event=cancel_event
            )
        except OSError as error:
            GLib.idle_add(self._show_result, generation, str(error), 1, False, False)
            return
        GLib.idle_add(
            self._show_result,
            generation,
            result.output or "(program finished without output)",
            result.returncode,
            result.timed_out,
            result.cancelled,
        )

    def _show_result(self, generation, text, returncode, timed_out, cancelled):
        if generation != self._run_generation:
            return GLib.SOURCE_REMOVE
        self.output.get_buffer().set_text(text)
        if cancelled:
            self.status.set_text("Stopped")
        elif timed_out:
            self.status.set_text("Program timed out")
        elif returncode != 0:
            lines = re.findall(r'File "[^"]+", line (\d+)', text)
            if lines:
                self._goto_line(int(lines[-1]))
                self.status.set_text("Program returned an error on line %s" % lines[-1])
            else:
                self.status.set_text("Program returned an error")
        else:
            self.status.set_text("Finished")
        self.run_button.set_sensitive(True)
        self.stop_button.set_sensitive(False)
        self._cancel_event = None
        return GLib.SOURCE_REMOVE

    def _stop_program(self, _button):
        if self._cancel_event is not None:
            self.status.set_text("Stopping…")
            self._cancel_event.set()

    def _goto_line(self, number):
        buffer = self.editor.get_buffer()
        found = buffer.get_iter_at_line(max(0, number - 1))
        where = found[1] if isinstance(found, tuple) else found
        end = where.copy()
        if not end.ends_line():
            end.forward_to_line_end()
        buffer.select_range(where, end)
        self.editor.scroll_to_iter(where, 0.2, False, 0, 0)

    def _editor_key(self, _controller, keyval, _keycode, state):
        buffer = self.editor.get_buffer()
        if keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter) and state & Gdk.ModifierType.CONTROL_MASK:
            self._run_program(None)
            return True
        if keyval == Gdk.KEY_Tab and not state & Gdk.ModifierType.SHIFT_MASK:
            buffer.insert_at_cursor("    ")
            return True
        if keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            cursor = buffer.get_iter_at_mark(buffer.get_insert())
            start = cursor.copy(); start.set_line_offset(0)
            line = buffer.get_text(start, cursor, False)
            indent = line[:len(line) - len(line.lstrip(" "))]
            if line.rstrip().endswith(":"):
                indent += "    "
            buffer.insert_at_cursor("\n" + indent)
            self.editor.scroll_mark_onscreen(buffer.get_insert())
            return True
        return False

    def _reset(self, _button):
        if self._cancel_event is not None:
            self._cancel_event.set()
        name = list(EXAMPLES)[self.examples.get_selected()]
        self._run_generation += 1
        self.run_button.set_sensitive(True)
        self.stop_button.set_sensitive(False)
        self._cancel_event = None
        self.editor.get_buffer().set_text(EXAMPLES[name])
        self.output.get_buffer().set_text(OUTPUT_PLACEHOLDER)
        self.status.set_text("Ready: %s example" % name)

    def read_file(self, file_path):
        """Restore a Python source buffer from a UTF-8 Journal object."""
        try:
            program = Path(file_path).read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            program = DEFAULT_PROGRAM
        self.editor.get_buffer().set_text(program)
        self.output.get_buffer().set_text(OUTPUT_PLACEHOLDER)
        self.status.set_text("Ready")
        self._run_generation += 1
        if self._cancel_event is not None:
            self._cancel_event.set()
        self._cancel_event = None
        self.run_button.set_sensitive(True)
        self.stop_button.set_sensitive(False)

    def write_file(self, file_path):
        """Save the Python source buffer as a UTF-8 Journal object."""
        Path(file_path).write_text(self._program(), encoding="utf-8")
