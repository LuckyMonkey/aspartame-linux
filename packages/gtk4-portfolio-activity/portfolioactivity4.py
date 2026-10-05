"""Native GTK4 Portfolio writing Activity."""

import json
from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity
from portfolio_export import write_html


class PortfolioActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("Portfolio"); self._build()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        root.set_margin_top(28); root.set_margin_bottom(28); root.set_margin_start(32); root.set_margin_end(32)
        root.set_hexpand(True); root.set_vexpand(True)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Portfolio editor"])
        title = Gtk.Label(label="Portfolio", xalign=0); title.add_css_class("title-1"); root.append(title)
        self.name = Gtk.Entry(); self.name.set_placeholder_text("Project title"); self.name.update_property([Gtk.AccessibleProperty.LABEL], ["Project title"]); root.append(self.name)
        self.body = Gtk.TextView(); self.body.set_wrap_mode(Gtk.WrapMode.WORD_CHAR); self.body.set_hexpand(True); self.body.set_vexpand(True); self.body.update_property([Gtk.AccessibleProperty.LABEL], ["Project description"])
        body_scroll = Gtk.ScrolledWindow(); body_scroll.set_min_content_height(320); body_scroll.set_hexpand(True); body_scroll.set_vexpand(True); body_scroll.set_child(self.body)
        body_surface = Gtk.Overlay(); body_surface.set_hexpand(True); body_surface.set_vexpand(True); body_surface.set_child(body_scroll)
        self.empty_state = Gtk.Label(label="Describe the project, what you made, and what you learned.", wrap=True); self.empty_state.add_css_class("editor-empty-state"); self.empty_state.set_halign(Gtk.Align.CENTER); self.empty_state.set_valign(Gtk.Align.CENTER); self.empty_state.set_can_target(False); self.empty_state.set_max_width_chars(48); body_surface.add_overlay(self.empty_state)
        self.body.get_buffer().connect("changed", self._body_changed)
        body_frame = Gtk.Frame(label="Project description"); body_frame.add_css_class("project-pane"); body_frame.set_hexpand(True); body_frame.set_vexpand(True); body_frame.set_child(body_surface); root.append(body_frame)
        self.status = Gtk.Label(label="Write about your project.", xalign=0); self.status.add_css_class("dim-label"); self.status.set_hexpand(True)
        footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8); footer.append(self.status)
        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        controls.set_halign(Gtk.Align.END)
        export = Gtk.Button(label="Export HTML")
        export.set_tooltip_text("Export this project as a portable HTML document")
        export.update_property([Gtk.AccessibleProperty.LABEL], ["Export project as HTML"])
        export.connect("clicked", self._export_html)
        controls.append(export)
        save = Gtk.Button(label="Save draft"); save.connect("clicked", self._save); controls.append(save)
        clear = Gtk.Button(label="Clear"); clear.connect("clicked", self._clear); controls.append(clear); footer.append(controls); root.append(footer)
        self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"entry { min-height: 42px; } frame.project-pane { border: 2px solid #8aa8b8; border-radius: 10px; padding: 8px; } scrolledwindow { border: 1px solid #8aa8b8; border-radius: 8px; } textview { padding: 14px; } label.editor-empty-state { background: #f1f5f7; border-radius: 12px; padding: 18px 24px; color: #52636b; } button { min-height: 42px; border-radius: 19px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _body_changed(self, _buffer):
        start, end = self.body.get_buffer().get_bounds()
        self.empty_state.set_visible(not self.body.get_buffer().get_text(start, end, False).strip())

    def _save(self, _button):
        title = self.name.get_text().strip() or "Untitled project"
        self.save()
        self.status.set_text("Draft saved: %s" % title)

    def _clear(self, _button):
        self.name.set_text(""); self.body.get_buffer().set_text(""); self.status.set_text("Write about your project.")

    def _export_html(self, _button):
        Gtk.FileDialog(title="Export Portfolio HTML").save(self, None, self._export_html_chosen)

    def _export_html_chosen(self, dialog, result):
        try:
            file_obj = dialog.save_finish(result)
            path = file_obj.get_path() if file_obj is not None else None
            if not path:
                return
            buffer = self.body.get_buffer()
            start, end = buffer.get_bounds()
            write_html(path, self.name.get_text(), buffer.get_text(start, end, False))
        except Exception as error:
            self.status.set_text("Export failed: %s" % error)
            return
        self.status.set_text("Exported HTML: %s" % (self.name.get_text().strip() or "Untitled project"))

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
