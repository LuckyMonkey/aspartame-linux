"""Native GTK4 Portfolio writing Activity."""

import json
from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class PortfolioActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("Portfolio"); self._build()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        root.set_margin_top(28); root.set_margin_bottom(28); root.set_margin_start(32); root.set_margin_end(32)
        root.set_hexpand(True); root.set_vexpand(True)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Portfolio editor"])
        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        body.set_hexpand(True); body.set_vexpand(True)
        body.set_halign(Gtk.Align.FILL); body.set_valign(Gtk.Align.FILL)
        root.append(body)
        title = Gtk.Label(label="Portfolio", xalign=0); title.add_css_class("title-1"); body.append(title)
        self.name = Gtk.Entry(); self.name.set_placeholder_text("Project title"); self.name.update_property([Gtk.AccessibleProperty.LABEL], ["Project title"]); body.append(self.name)
        self.body = Gtk.TextView(); self.body.set_wrap_mode(Gtk.WrapMode.WORD_CHAR); self.body.set_hexpand(True); self.body.set_vexpand(True); self.body.update_property([Gtk.AccessibleProperty.LABEL], ["Project description"])
        body_scroll = Gtk.ScrolledWindow(); body_scroll.set_min_content_height(320); body_scroll.set_hexpand(True); body_scroll.set_vexpand(True); body_scroll.set_child(self.body)
        body_frame = Gtk.Frame(label="Project description"); body_frame.set_hexpand(True); body_frame.set_vexpand(True); body_frame.set_child(body_scroll); body.append(body_frame)
        self.status = Gtk.Label(label="Write about your project.", xalign=0); self.status.add_css_class("dim-label"); body.append(self.status)
        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        save = Gtk.Button(label="Save draft"); save.connect("clicked", self._save); controls.append(save)
        clear = Gtk.Button(label="Clear"); clear.connect("clicked", self._clear); controls.append(clear); body.append(controls)
        self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"entry { min-height: 42px; } scrolledwindow { border: 1px solid #8aa8b8; border-radius: 8px; } textview { padding: 14px; } button { min-height: 42px; border-radius: 19px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _save(self, _button):
        title = self.name.get_text().strip() or "Untitled project"; self.status.set_text("Draft saved: %s" % title)

    def _clear(self, _button):
        self.name.set_text(""); self.body.get_buffer().set_text(""); self.status.set_text("Write about your project.")

    def read_file(self, file_path):
        """Restore project title and description from a Journal object."""
        try:
            payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
            payload = {}
        title = str(payload.get("title", "")) if isinstance(payload, dict) else ""
        body = str(payload.get("body", "")) if isinstance(payload, dict) else ""
        self.name.set_text(title)
        self.body.get_buffer().set_text(body)
        self.status.set_text("Draft restored: %s" % (title or "Untitled project"))

    def write_file(self, file_path):
        """Save project title and description as a JSON Journal object."""
        buffer = self.body.get_buffer()
        start, end = buffer.get_bounds()
        Path(file_path).write_text(json.dumps({"title": self.name.get_text(), "body": buffer.get_text(start, end, False)}, sort_keys=True) + "\n", encoding="utf-8")
