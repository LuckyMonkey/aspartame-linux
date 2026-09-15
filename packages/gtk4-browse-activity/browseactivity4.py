"""Bounded native GTK4 Browse Activity without a GTK3/WebKit import."""
import re
import threading
import urllib.request

from gi.repository import Gdk, GLib, Gtk
from sugar4.activity import SimpleActivity


class BrowseActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Browse")
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        root.set_margin_start(24); root.set_margin_end(24)
        root.set_margin_top(20); root.set_margin_bottom(20)
        root.add_css_class("browse-root")
        title = Gtk.Label(label="Browse", xalign=0); title.add_css_class("title-1"); root.append(title)
        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.url = Gtk.Entry(placeholder_text="https://example.org")
        self.url.set_hexpand(True); self.url.update_property([Gtk.AccessibleProperty.LABEL], ["Web address"])
        self.url.connect("activate", self._load); controls.append(self.url)
        go = Gtk.Button(label="Go"); go.update_property([Gtk.AccessibleProperty.LABEL], ["Load web address"]); go.connect("clicked", self._load); controls.append(go)
        root.append(controls)
        self.status = Gtk.Label(label="Enter a web address and press Enter", xalign=0); self.status.add_css_class("dim-label"); root.append(self.status)
        self.page = Gtk.TextView(editable=False, wrap_mode=Gtk.WrapMode.WORD_CHAR)
        self.page.update_property([Gtk.AccessibleProperty.LABEL], ["Web page content"]); self.page.set_vexpand(True)
        self.page.get_buffer().set_text("Welcome to Browse.\n\nThis native GTK4 surface keeps web content inside Sugar's Activity lifecycle.")
        scroll = Gtk.ScrolledWindow(); scroll.set_child(self.page); scroll.set_vexpand(True); root.append(scroll)
        self.set_canvas(root); self._install_css(); self.url.grab_focus()

    def _install_css(self):
        provider = Gtk.CssProvider(); provider.load_from_data(b".browse-root { background: #111; color: #f5f5f5; } .browse-root label { color: #f5f5f5; } textview { background: #050505; color: #f5f5f5; padding: 14px; } entry { min-height: 38px; } button { min-height: 38px; border-radius: 18px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _load(self, widget):
        address = self.url.get_text().strip()
        if not address: return
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", address): address = "https://" + address
        self.url.set_text(address); self.status.set_text("Loading…")
        threading.Thread(target=self._fetch, args=(address,), daemon=True).start()

    def _fetch(self, address):
        try:
            with urllib.request.urlopen(address, timeout=10) as response:
                body = response.read(32768).decode("utf-8", "replace")
            title = re.search(r"<title[^>]*>(.*?)</title>", body, re.I | re.S)
            heading = re.sub(r"\s+", " ", title.group(1)).strip() if title else address
            text = re.sub(r"<[^>]+>", " ", body); text = re.sub(r"\s+", " ", text).strip()
            message = "%s\n\n%s" % (heading, text[:4000])
            GLib.idle_add(self._show, "Loaded", message)
        except Exception as error:
            GLib.idle_add(self._show, "Load failed: %s" % error, "Unable to load this address. Check the URL or network connection.")

    def _show(self, status, text):
        self.status.set_text(status); self.page.get_buffer().set_text(text); return GLib.SOURCE_REMOVE
