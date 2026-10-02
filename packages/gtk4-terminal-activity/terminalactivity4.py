"""Native GTK4 Terminal Activity.

The old bundle imported GTK3 Vte before the GTK4 activity process was ready.
This port keeps the Sugar Activity identity and never mixes GI namespaces.

Two backends, chosen at start:

* **VTE (GTK4, ``Vte 3.91``)** — the image ships ``vte4``.  A real terminal
  emulator with tabs, copy/paste (Ctrl+Shift+C/V), zoom (Ctrl+=/Ctrl+-),
  10,000 lines of scrollback, and a restart button when the shell exits.  This
  matches what GTK3 Terminal users expect.
* **Command runner** — used only when VTE for GTK4 is missing.  Commands are
  entered in a GTK4 entry and their captured output is shown read-only, as the
  first port did.

Both keep the "Shell command" entry (in VTE mode it types the command into
the active tab), so keyboard-only and AT-SPI users always have a named target.

Journal payload (v1, 2026-10-02): JSON with each tab's working directory and
the tail of its scrollback.  Resuming opens the tabs in those directories and
shows the saved text above a fresh shell; old shells are not resurrected.
"""

import json
import os
import subprocess
from pathlib import Path

import gi
from gi.repository import Gdk, GLib, Gtk
from sugar4.activity import SimpleActivity

try:
    gi.require_version("Vte", "3.91")
    from gi.repository import Vte
except (ValueError, ImportError):  # VTE for GTK4 is not installed
    Vte = None


BANNER = "Aspartame GTK4 Terminal"
SCROLLBACK_LINES = 10000
SAVED_LINES = 2000
MAX_TABS = 8
FONT_SCALES = (0.8, 0.9, 1.0, 1.1, 1.25, 1.5, 1.75, 2.0)
FORMAT_VERSION = 1


def _shell():
    return os.environ.get("SHELL") or "/bin/bash"


class TerminalActivity(SimpleActivity):
    # Read by the host harness: a resumed tab shows a marker and a new prompt,
    # so its next save differs from the one it was resumed from.
    VOLATILE_SAVE_REASON = "a live shell adds a resume marker and prompt to scrollback"

    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Terminal")
        self.backend = "vte" if Vte is not None else "runner"
        self._scale = FONT_SCALES.index(1.0)
        self._tabs = []
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        root.set_margin_start(24); root.set_margin_end(24)
        root.set_margin_top(20); root.set_margin_bottom(20)
        root.add_css_class("terminal-root")

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        title = Gtk.Label(label="Terminal", xalign=0)
        title.add_css_class("title-1"); title.set_hexpand(True)
        header.append(title)
        if self.backend == "vte":
            for label, tip, callback in (("New tab", "Open a new tab (Ctrl+Shift+T)", self._new_tab_clicked),
                                         ("Copy", "Copy selection (Ctrl+Shift+C)", self._copy),
                                         ("Paste", "Paste (Ctrl+Shift+V)", self._paste),
                                         ("A−", "Smaller text (Ctrl+−)", lambda: self._zoom(-1)),
                                         ("A+", "Larger text (Ctrl+=)", lambda: self._zoom(1))):
                header.append(self._button(label, tip, callback))
        root.append(header)

        if self.backend == "vte":
            self.notebook = Gtk.Notebook(scrollable=True)
            self.notebook.set_vexpand(True)
            self.notebook.update_property([Gtk.AccessibleProperty.LABEL], ["Terminal tabs"])
            root.append(self.notebook)
        else:
            self.output = Gtk.TextView(editable=False, monospace=True, wrap_mode=Gtk.WrapMode.WORD_CHAR)
            self.output.update_property([Gtk.AccessibleProperty.LABEL], ["Terminal output"])
            self.output.set_vexpand(True); self.output.set_hexpand(True)
            self.output.set_top_margin(12); self.output.set_bottom_margin(12)
            self.output.get_buffer().set_text(BANNER + "\n$ ")
            scroll = Gtk.ScrolledWindow(); scroll.set_child(self.output); scroll.set_vexpand(True)
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
        if self.backend == "vte":
            self._install_shortcuts(root)
            self._add_tab()
        else:
            self.command.grab_focus()

    def _button(self, label, tip, callback):
        button = Gtk.Button(label=label)
        button.set_tooltip_text(tip)
        button.update_property([Gtk.AccessibleProperty.LABEL, Gtk.AccessibleProperty.DESCRIPTION],
                               [tip.split(" (")[0], tip])
        button.connect("clicked", lambda _b: callback())
        return button

    def _install_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(b".terminal-root { background: #111; color: #f5f5f5; } .terminal-root label { color: #f5f5f5; } textview { background: #050505; color: #f5f5f5; padding: 12px; } entry { min-height: 38px; } button { min-height: 38px; border-radius: 18px; }")
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _install_shortcuts(self, widget):
        controller = Gtk.ShortcutController()
        controller.set_scope(Gtk.ShortcutScope.MANAGED)
        for accel, callback in (("<Control><Shift>c", self._copy), ("<Control><Shift>v", self._paste),
                                ("<Control><Shift>t", self._new_tab_clicked),
                                ("<Control><Shift>w", self._close_current),
                                ("<Control>equal", lambda: self._zoom(1)), ("<Control>plus", lambda: self._zoom(1)),
                                ("<Control>minus", lambda: self._zoom(-1))):
            action = Gtk.CallbackAction.new(lambda *_a, cb=callback: (cb(), True)[1])
            controller.add_shortcut(Gtk.Shortcut.new(Gtk.ShortcutTrigger.parse_string(accel), action))
        widget.add_controller(controller)

    # -- VTE tabs --------------------------------------------------------

    def _add_tab(self, cwd=None, history=""):
        if len(self._tabs) >= MAX_TABS:
            return None
        terminal = Vte.Terminal()
        terminal.set_scrollback_lines(SCROLLBACK_LINES)
        terminal.set_font_scale(FONT_SCALES[self._scale])
        terminal.set_hexpand(True); terminal.set_vexpand(True)
        terminal.update_property([Gtk.AccessibleProperty.LABEL], ["Terminal"])
        foreground, background = Gdk.RGBA(), Gdk.RGBA()
        foreground.parse("#f5f5f5"); background.parse("#050505")
        terminal.set_colors(foreground, background, None)
        tab = {"terminal": terminal, "pid": None, "cwd": cwd if cwd and os.path.isdir(cwd) else os.path.expanduser("~")}
        scroll = Gtk.ScrolledWindow(); scroll.set_child(terminal)
        label = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        tab["label"] = Gtk.Label(label=os.path.basename(tab["cwd"]) or "/")
        label.append(tab["label"])
        close = Gtk.Button(icon_name="window-close-symbolic")
        close.add_css_class("flat")
        close.update_property([Gtk.AccessibleProperty.LABEL], ["Close tab"])
        close.connect("clicked", lambda _b, t=tab: self._close_tab(t))
        label.append(close)
        tab["page"] = scroll
        self._tabs.append(tab)
        self.notebook.append_page(scroll, label)
        self.notebook.set_current_page(self.notebook.page_num(scroll))
        terminal.feed(((history.rstrip("\n").replace("\n", "\r\n") + "\r\n\x1b[2m-- resumed --\x1b[0m\r\n")
                       if history else BANNER + "\r\n").encode("utf-8"))
        terminal.connect("child-exited", self._child_exited, tab)
        self._spawn(tab)
        terminal.grab_focus()
        return tab

    def _spawn(self, tab):
        tab["terminal"].spawn_async(
            Vte.PtyFlags.DEFAULT, tab["cwd"], [_shell()], [], GLib.SpawnFlags.DEFAULT,
            None, None, -1, None, self._spawned, tab)

    def _spawned(self, terminal, pid, error, tab):
        if error is not None or pid < 0:
            terminal.feed(("Could not start %s: %s\r\n" % (_shell(), error.message if error else "unknown error")).encode())
            return
        tab["pid"] = pid

    def _child_exited(self, terminal, status, tab):
        tab["pid"] = None
        terminal.feed(b"\r\n\x1b[2m[shell exited - type in the Shell command box or press New tab]\x1b[0m\r\n")

    def _current_tab(self):
        page = self.notebook.get_nth_page(self.notebook.get_current_page()) if self._tabs else None
        return next((tab for tab in self._tabs if tab["page"] is page), None)

    def _new_tab_clicked(self):
        current = self._current_tab()
        self._add_tab(cwd=self._cwd(current) if current else None)

    def _close_current(self):
        current = self._current_tab()
        if current is not None:
            self._close_tab(current)

    def _close_tab(self, tab):
        if tab["pid"]:
            try:
                os.kill(tab["pid"], 1)  # SIGHUP, as closing a terminal does
            except OSError:
                pass
        self.notebook.remove_page(self.notebook.page_num(tab["page"]))
        self._tabs.remove(tab)
        if not self._tabs:
            self._add_tab()

    def _cwd(self, tab):
        uri = tab["terminal"].get_current_directory_uri()
        if uri:
            try:
                return GLib.filename_from_uri(uri)[0]
            except GLib.Error:
                pass
        if tab["pid"]:
            try:
                return os.readlink("/proc/%d/cwd" % tab["pid"])
            except OSError:
                pass
        return tab["cwd"]

    def _copy(self):
        tab = self._current_tab()
        if tab and tab["terminal"].get_has_selection():
            tab["terminal"].copy_clipboard_format(Vte.Format.TEXT)

    def _paste(self):
        # Read through GDK rather than Vte.Terminal.paste_clipboard(), which
        # crashes VTE 0.76 when the terminal is not realized yet.
        tab = self._current_tab()
        if tab:
            self.get_clipboard().read_text_async(None, self._pasted, tab)

    def _pasted(self, clipboard, result, tab):
        try:
            text = clipboard.read_text_finish(result)
        except GLib.Error:
            return
        if text and tab in self._tabs:
            tab["terminal"].paste_text(text)

    def _zoom(self, step):
        self._scale = max(0, min(len(FONT_SCALES) - 1, self._scale + step))
        for tab in self._tabs:
            tab["terminal"].set_font_scale(FONT_SCALES[self._scale])

    # -- shared controls -------------------------------------------------

    def _append(self, text):
        buffer = self.output.get_buffer()
        buffer.insert(buffer.get_end_iter(), text)
        self.output.scroll_to_iter(buffer.get_end_iter(), 0, False, 0, 0)

    def _run_command(self, entry):
        command = entry.get_text().strip()
        if not command:
            return
        entry.set_text("")
        if self.backend == "vte":
            tab = self._current_tab()
            if tab is None or tab["pid"] is None:
                tab = self._add_tab(cwd=self._cwd(tab) if tab else None)
            if tab is not None:
                tab["terminal"].feed_child((command + "\n").encode("utf-8"))
            return
        try:
            result = subprocess.run(command, shell=True, text=True, capture_output=True, timeout=10, check=False)
            output = result.stdout + result.stderr
            self._append("$ " + command + "\n" + (output or "(no output)\n"))
            if result.returncode:
                self._append("[exit %d]\n" % result.returncode)
        except subprocess.TimeoutExpired:
            self._append("$ %s\n[command timed out after 10 seconds]\n" % command)

    def _clear(self, _button):
        if self.backend == "vte":
            tab = self._current_tab()
            if tab:
                tab["terminal"].reset(True, True)
        else:
            self.output.get_buffer().set_text(BANNER + "\n$ ")

    # -- Journal ---------------------------------------------------------

    def _transcript(self, tab):
        terminal = tab["terminal"]
        text = terminal.get_text_format(Vte.Format.TEXT) if hasattr(terminal, "get_text_format") else ""
        lines = (text or "").rstrip("\n").split("\n")
        return "\n".join(lines[-SAVED_LINES:])

    def write_file(self, file_path):
        if self.backend == "vte":
            tabs = [{"cwd": self._cwd(tab), "scrollback": self._transcript(tab)} for tab in self._tabs]
        else:
            start, end = self.output.get_buffer().get_bounds()
            tabs = [{"cwd": os.getcwd(), "scrollback": self.output.get_buffer().get_text(start, end, False)}]
        state = {"version": FORMAT_VERSION, "backend": self.backend, "tabs": tabs}
        Path(file_path).write_text(json.dumps(state, sort_keys=True) + "\n", encoding="utf-8")

    def read_file(self, file_path):
        """Reopen saved tabs in their directories with their scrollback shown."""
        try:
            state = json.loads(Path(file_path).read_text(encoding="utf-8"))
            tabs = state.get("tabs") if isinstance(state, dict) else None
            if not isinstance(tabs, list):
                raise ValueError("no tabs")
            tabs = [t for t in tabs if isinstance(t, dict)][:MAX_TABS]
        except (OSError, ValueError, TypeError):
            return
        if not tabs:
            return
        if self.backend == "vte":
            for tab in list(self._tabs):
                self.notebook.remove_page(self.notebook.page_num(tab["page"]))
                if tab["pid"]:
                    try:
                        os.kill(tab["pid"], 1)
                    except OSError:
                        pass
            self._tabs = []
            for saved in tabs:
                self._add_tab(cwd=str(saved.get("cwd") or ""), history=str(saved.get("scrollback") or ""))
        else:
            self.output.get_buffer().set_text(str(tabs[0].get("scrollback") or (BANNER + "\n$ ")))
