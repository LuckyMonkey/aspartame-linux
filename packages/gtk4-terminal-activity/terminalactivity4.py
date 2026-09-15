"""Bounded native GTK4 Terminal Activity.

The old bundle imported GTK3 Vte before the GTK4 activity process was ready.
This implementation keeps the Sugar Activity identity and provides a useful
local shell without mixing GI namespaces: commands are entered in GTK4 and
their captured output is rendered in a read-only GTK4 text view.
"""

import subprocess

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class TerminalActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Terminal")
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        root.set_margin_start(24)
        root.set_margin_end(24)
        root.set_margin_top(20)
        root.set_margin_bottom(20)
        root.add_css_class("terminal-root")

        title = Gtk.Label(label="Terminal", xalign=0)
        title.add_css_class("title-1")
        root.append(title)

        self.output = Gtk.TextView(editable=False, monospace=True, wrap_mode=Gtk.WrapMode.WORD_CHAR)
        self.output.update_property([Gtk.AccessibleProperty.LABEL], ["Terminal output"])
        self.output.set_vexpand(True)
        self.output.set_hexpand(True)
        self.output.set_top_margin(12)
        self.output.set_bottom_margin(12)
        self.output.get_buffer().set_text("Aspartame GTK4 Terminal\n$ ")
        scroll = Gtk.ScrolledWindow()
        scroll.set_child(self.output)
        scroll.set_vexpand(True)
        root.append(scroll)

        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.command = Gtk.Entry(placeholder_text="Enter a command")
        self.command.set_hexpand(True)
        self.command.update_property([Gtk.AccessibleProperty.LABEL], ["Shell command"])
        self.command.connect("activate", self._run_command)
        controls.append(self.command)
        clear = Gtk.Button(label="Clear")
        clear.update_property([Gtk.AccessibleProperty.LABEL], ["Clear terminal output"])
        clear.connect("clicked", self._clear)
        controls.append(clear)
        root.append(controls)
        self.set_canvas(root)
        self._install_css()
        self.command.grab_focus()

    def _install_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(b".terminal-root { background: #111; color: #f5f5f5; } .terminal-root label { color: #f5f5f5; } textview { background: #050505; color: #f5f5f5; padding: 12px; } entry { min-height: 38px; } button { min-height: 38px; border-radius: 18px; }")
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _append(self, text):
        buffer = self.output.get_buffer()
        end = buffer.get_end_iter()
        buffer.insert(end, text)
        self.output.scroll_to_iter(buffer.get_end_iter(), 0, False, 0, 0)

    def _run_command(self, entry):
        command = entry.get_text().strip()
        if not command:
            return
        entry.set_text("")
        try:
            result = subprocess.run(command, shell=True, text=True, capture_output=True, timeout=10, check=False)
            output = result.stdout + result.stderr
            self._append("$ " + command + "\n" + (output or "(no output)\n"))
            if result.returncode:
                self._append("[exit %d]\n" % result.returncode)
        except subprocess.TimeoutExpired:
            self._append("$ %s\n[command timed out after 10 seconds]\n" % command)

    def _clear(self, _button):
        self.output.get_buffer().set_text("Aspartame GTK4 Terminal\n$ ")

