"""Small, offline GTK4 Python playground for Sugar.

Closer to GTK3 Pippy than the first port: a library of examples, Run and Stop
(programs run in a separate isolated Python process and can be stopped at any
time), text typed into "Program input" is given to the program, output streams
while the program runs, Tab/Enter follow Python indentation, and an error
jumps the cursor to the failing line.  Syntax colouring, Pygame/Sugar
examples, and exporting a program as an Activity bundle remain unported.

The Journal payload is unchanged: the plain UTF-8 program text.
"""

import os
import re
import signal
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
EXAMPLES = {
    "Hello": DEFAULT_PROGRAM,
    "Times table": '''number = 7
for row in range(1, 11):
    print(number, "x", row, "=", number * row)
''',
    "Guess the number": '''import random
import sys

secret = random.randint(1, 20)
# Type guesses in "Program input", separated by ;, then press Run.
for line in sys.stdin:
    if not line.strip():
        continue
    guess = int(line)
    if guess == secret:
        print(guess, "is right!")
        break
    print(guess, "is too", "low" if guess < secret else "high")
else:
    print("Out of guesses. It was", secret)
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
    "Primes": '''def is_prime(n):
    if n < 2:
        return False
    for d in range(2, int(n ** 0.5) + 1):
        if n % d == 0:
            return False
    return True

print([n for n in range(100) if is_prime(n)])
''',
}
MAX_OUTPUT = 200_000


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
        keys = Gtk.EventControllerKey()
        keys.connect("key-pressed", self._editor_key)
        self.editor.add_controller(keys)
        editor_scroll = Gtk.ScrolledWindow()
        editor_scroll.set_min_content_height(260)
        editor_scroll.set_vexpand(True)
        editor_scroll.set_child(self.editor)
        root.append(editor_scroll)

        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.run = Gtk.Button(label="Run")
        self.run.add_css_class("suggested-action")
        self.run.set_tooltip_text("Run the program (Ctrl+Enter)")
        self.run.connect("clicked", self._run_program)
        controls.append(self.run)
        self.stop = Gtk.Button(label="Stop")
        self.stop.set_tooltip_text("Stop the running program")
        self.stop.update_property([Gtk.AccessibleProperty.LABEL], ["Stop the program"])
        self.stop.set_sensitive(False)
        self.stop.connect("clicked", lambda _b: self._stop_program())
        controls.append(self.stop)
        self.examples = Gtk.DropDown.new_from_strings(list(EXAMPLES))
        self.examples.set_tooltip_text("Examples")
        self.examples.update_property([Gtk.AccessibleProperty.LABEL], ["Examples"])
        controls.append(self.examples)
        reset = Gtk.Button(label="Reset example")
        reset.set_tooltip_text("Replace the program with the chosen example")
        reset.connect("clicked", self._reset)
        controls.append(reset)
        root.append(controls)

        self.stdin = Gtk.Entry(placeholder_text="Program input (separate lines with ;)")
        self.stdin.update_property([Gtk.AccessibleProperty.LABEL], ["Program input"])
        root.append(self.stdin)
        self._process = None

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

    def _run_program(self, _button=None):
        if self._process is not None:
            return
        self.output.get_buffer().set_text("")
        self.status.set_text("Running…")
        stdin = "\n".join(part.strip() for part in self.stdin.get_text().split(";")) + "\n"
        try:
            self._process = subprocess.Popen(
                [sys.executable, "-I", "-u", "-c", self._program()],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, start_new_session=True)
        except OSError as error:
            self._show_result(str(error), 1)
            return
        self.run.set_sensitive(False)
        self.stop.set_sensitive(True)
        threading.Thread(target=self._execute, args=(self._process, stdin), daemon=True).start()

    def _execute(self, process, stdin):
        try:
            process.stdin.write(stdin)
            process.stdin.close()
        except OSError:
            pass
        size = 0
        for line in process.stdout:
            size += len(line)
            if size > MAX_OUTPUT:
                GLib.idle_add(self._append, "\n[output cut off: too long]\n")
                self._stop_program()
                break
            GLib.idle_add(self._append, line)
        GLib.idle_add(self._show_result, None, process.wait())

    def _append(self, text):
        buffer = self.output.get_buffer()
        buffer.insert(buffer.get_end_iter(), text)
        return GLib.SOURCE_REMOVE

    def _stop_program(self):
        process = self._process
        if process is not None and process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except OSError:
                pass

    def _show_result(self, text, returncode):
        buffer = self.output.get_buffer()
        if text is not None:
            buffer.set_text(text)
        start, end = buffer.get_bounds()
        output = buffer.get_text(start, end, False)
        if not output:
            buffer.set_text("(program finished without output)")
        self._process = None
        self.run.set_sensitive(True)
        self.stop.set_sensitive(False)
        if returncode == 0:
            self.status.set_text("Finished")
        elif returncode in (-signal.SIGTERM, -signal.SIGKILL):
            self.status.set_text("Stopped")
        else:
            lines = re.findall(r'File "<string>", line (\d+)', output)
            if lines:
                self._goto_line(int(lines[-1]))
                self.status.set_text("Program returned an error on line %s" % lines[-1])
            else:
                self.status.set_text("Program returned an error")
        return GLib.SOURCE_REMOVE

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
            self._run_program()
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
        name = list(EXAMPLES)[self.examples.get_selected()]
        self.editor.get_buffer().set_text(EXAMPLES[name])
        self.output.get_buffer().set_text("")
        self.status.set_text("Ready: %s example" % name)

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
