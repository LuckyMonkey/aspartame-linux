"""Native GTK4 Browse Activity.

Two backends, chosen at start:

* **WebKit (``WebKit 6.0``)** — the image ships ``webkitgtk-6.0``.  Real web
  pages with tabs, back/forward, reload/stop, a load progress bar, zoom,
  bookmarks, and downloads saved to the user's Downloads folder (named in the
  status line; GTK3 Browse put downloads in the Journal, which is not ported).
* **Text fetcher** — used only when WebKit for GTK4 is missing: the page is
  fetched and its text shown read-only, as the first port did.

The "Web address" entry, "Load web address" button, and a status line that
says "Loaded" or "Load failed" exist in both backends; the guest probe and
keyboard users rely on them.

Journal payload (v1, 2026-10-02): JSON with the open tabs' addresses and
titles, the current tab, and bookmarks.  Resuming reopens those tabs.
Collaboration (shared browsing) is not ported.
"""

import html
import json
import os
import re
import threading
import urllib.request
from pathlib import Path

import gi
from gi.repository import Gdk, GLib, Gtk
from sugar4.activity import SimpleActivity

try:
    gi.require_version("WebKit", "6.0")
    from gi.repository import WebKit
except (ValueError, ImportError):  # WebKit for GTK4 is not installed
    WebKit = None


WELCOME = "Welcome to Browse."
WELCOME_HTML = """<!DOCTYPE html><html><head><meta charset="utf-8"><title>Browse</title>
<style>body{font-family:sans-serif;background:#111;color:#f5f5f5;margin:48px;font-size:18px}
h1{font-size:32px}</style></head><body><h1>%s</h1>
<p>Type a web address above and press Enter. Pages open inside this Activity, and
Stop keeps your tabs and bookmarks in the Journal.</p></body></html>""" % WELCOME
HOME_URI = "about:blank"
MAX_TABS = 8
ZOOM_STEPS = (0.5, 0.67, 0.8, 0.9, 1.0, 1.1, 1.25, 1.5, 1.75, 2.0)
FORMAT_VERSION = 1


def normalize_address(address):
    address = address.strip()
    if not address:
        return ""
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", address):
        return address
    if " " in address or "." not in address:
        # Not an address: search for it.
        return "https://duckduckgo.com/html/?q=" + urllib.request.quote(address)
    return "https://" + address


class BrowseActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Browse")
        self.backend = "webkit" if WebKit is not None else "text"
        self._tabs = []
        self.bookmarks = []
        self._downloads_hooked = False
        self._zoom = ZOOM_STEPS.index(1.0)
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        root.set_margin_start(24); root.set_margin_end(24)
        root.set_margin_top(20); root.set_margin_bottom(20)
        root.add_css_class("browse-root")
        title = Gtk.Label(label="Browse", xalign=0); title.add_css_class("title-1"); root.append(title)

        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        if self.backend == "webkit":
            self.back = self._button("go-previous-symbolic", "Back (Alt+Left)", self._go_back)
            self.forward = self._button("go-next-symbolic", "Forward (Alt+Right)", self._go_forward)
            self.reload = self._button("view-refresh-symbolic", "Reload (F5 or Ctrl+R)", self._reload_or_stop)
            for button in (self.back, self.forward, self.reload):
                controls.append(button)
        self.url = Gtk.Entry(placeholder_text="Web address or search words")
        self.url.set_hexpand(True); self.url.update_property([Gtk.AccessibleProperty.LABEL], ["Web address"])
        self.url.connect("activate", self._load); controls.append(self.url)
        go = Gtk.Button(label="Go"); go.update_property([Gtk.AccessibleProperty.LABEL], ["Load web address"])
        go.connect("clicked", self._load); controls.append(go)
        if self.backend == "webkit":
            controls.append(self._button("tab-new-symbolic", "New tab (Ctrl+T)", self._new_tab))
            controls.append(self._button("starred-symbolic", "Bookmark this page (Ctrl+D)", self._bookmark))
            self.bookmark_menu = Gtk.MenuButton(icon_name="user-bookmarks-symbolic")
            self.bookmark_menu.set_tooltip_text("Bookmarks")
            self.bookmark_menu.update_property([Gtk.AccessibleProperty.LABEL], ["Bookmarks"])
            self.bookmark_list = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE)
            self.bookmark_list.set_activate_on_single_click(True)
            self.bookmark_list.connect("row-activated", self._bookmark_opened)
            popover = Gtk.Popover(); popover.set_child(self.bookmark_list)
            self.bookmark_menu.set_popover(popover)
            controls.append(self.bookmark_menu)
            controls.append(self._button("zoom-out-symbolic", "Zoom out (Ctrl+−)", lambda: self._zoom_by(-1)))
            controls.append(self._button("zoom-in-symbolic", "Zoom in (Ctrl+=)", lambda: self._zoom_by(1)))
        root.append(controls)

        self.status = Gtk.Label(label=WELCOME + " Enter a web address and press Enter", xalign=0)
        self.status.add_css_class("dim-label")
        self.status.update_property([Gtk.AccessibleProperty.LABEL], ["Browse status"])
        root.append(self.status)

        if self.backend == "webkit":
            self.progress = Gtk.ProgressBar(); self.progress.set_visible(False)
            root.append(self.progress)
            self.notebook = Gtk.Notebook(scrollable=True)
            self.notebook.set_vexpand(True)
            self.notebook.update_property([Gtk.AccessibleProperty.LABEL], ["Browse tabs"])
            self.notebook.connect("switch-page", self._switched)
            root.append(self.notebook)
            self._install_shortcuts(root)
            self._refresh_bookmarks()
        else:
            self.page = Gtk.TextView(editable=False, wrap_mode=Gtk.WrapMode.WORD_CHAR)
            self.page.update_property([Gtk.AccessibleProperty.LABEL], ["Web page content"]); self.page.set_vexpand(True)
            self.page.get_buffer().set_text(WELCOME + "\n\nThis native GTK4 surface keeps web content inside Sugar's Activity lifecycle.")
            scroll = Gtk.ScrolledWindow(); scroll.set_child(self.page); scroll.set_vexpand(True); root.append(scroll)
        self.set_canvas(root); self._install_css()
        if self.backend == "webkit":
            self._add_tab()
        self.url.grab_focus()

    def _button(self, icon, tip, callback):
        button = Gtk.Button(icon_name=icon)
        button.set_tooltip_text(tip)
        button.update_property([Gtk.AccessibleProperty.LABEL], [tip.split(" (")[0]])
        button.connect("clicked", lambda _b: callback())
        return button

    def _install_css(self):
        provider = Gtk.CssProvider(); provider.load_from_data(b".browse-root { background: #111; color: #f5f5f5; } .browse-root label { color: #f5f5f5; } textview { background: #050505; color: #f5f5f5; padding: 14px; } entry { min-height: 38px; } button { min-height: 38px; border-radius: 18px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _install_shortcuts(self, widget):
        controller = Gtk.ShortcutController()
        controller.set_scope(Gtk.ShortcutScope.MANAGED)
        for accel, callback in (("<Control>t", self._new_tab), ("<Control>w", self._close_current),
                                ("<Control>l", self._focus_address), ("<Control>d", self._bookmark),
                                ("<Control>r", self._reload_or_stop), ("F5", self._reload_or_stop),
                                ("<Alt>Left", self._go_back), ("<Alt>Right", self._go_forward),
                                ("<Control>equal", lambda: self._zoom_by(1)), ("<Control>plus", lambda: self._zoom_by(1)),
                                ("<Control>minus", lambda: self._zoom_by(-1)), ("<Control>0", lambda: self._zoom_by(0))):
            action = Gtk.CallbackAction.new(lambda *_a, cb=callback: (cb(), True)[1])
            controller.add_shortcut(Gtk.Shortcut.new(Gtk.ShortcutTrigger.parse_string(accel), action))
        widget.add_controller(controller)

    # -- WebKit tabs -----------------------------------------------------

    def _add_tab(self, uri=None, title=None):
        if len(self._tabs) >= MAX_TABS:
            self.status.set_text("Close a tab first; Browse keeps at most %d open." % MAX_TABS)
            return None
        view = WebKit.WebView()
        view.set_vexpand(True); view.set_hexpand(True)
        view.set_zoom_level(ZOOM_STEPS[self._zoom])
        view.update_property([Gtk.AccessibleProperty.LABEL], ["Web page"])
        tab = {"view": view, "label": Gtk.Label(label=title or "New tab", max_width_chars=18, ellipsize=3)}
        heading = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        heading.append(tab["label"])
        close = Gtk.Button(icon_name="window-close-symbolic"); close.add_css_class("flat")
        close.update_property([Gtk.AccessibleProperty.LABEL], ["Close tab"])
        close.connect("clicked", lambda _b, t=tab: self._close_tab(t))
        heading.append(close)
        view.connect("load-changed", self._load_changed, tab)
        view.connect("load-failed", self._load_failed, tab)
        view.connect("notify::title", self._title_changed, tab)
        view.connect("notify::estimated-load-progress", self._progress_changed, tab)
        if not self._downloads_hooked:
            view.get_network_session().connect("download-started", self._download_started)
            self._downloads_hooked = True
        self._tabs.append(tab)
        self.notebook.append_page(view, heading)
        self.notebook.set_current_page(self.notebook.page_num(view))
        if uri and uri != HOME_URI:
            view.load_uri(uri)
        else:
            view.load_html(WELCOME_HTML, None)
        return tab

    def _current(self):
        if not self._tabs:
            return None
        page = self.notebook.get_nth_page(self.notebook.get_current_page())
        return next((tab for tab in self._tabs if tab["view"] is page), None)

    def _new_tab(self):
        self._add_tab()
        self._focus_address()

    def _close_current(self):
        tab = self._current()
        if tab:
            self._close_tab(tab)

    def _close_tab(self, tab):
        tab["view"].stop_loading()
        self.notebook.remove_page(self.notebook.page_num(tab["view"]))
        self._tabs.remove(tab)
        if not self._tabs:
            self._add_tab()

    def _focus_address(self):
        self.url.grab_focus()
        self.url.select_region(0, -1)

    def _switched(self, _notebook, page, _number):
        tab = next((t for t in self._tabs if t["view"] is page), None)
        if tab:
            self._sync_toolbar(tab)

    def _tab_uri(self, tab):
        uri = tab["view"].get_uri() or HOME_URI
        return HOME_URI if uri.startswith(("about:", "data:")) else uri

    def _sync_toolbar(self, tab):
        view = tab["view"]
        uri = self._tab_uri(tab)
        self.url.set_text("" if uri == HOME_URI else uri)
        self.back.set_sensitive(view.can_go_back())
        self.forward.set_sensitive(view.can_go_forward())
        loading = view.is_loading() if hasattr(view, "is_loading") else False
        self.reload.set_icon_name("process-stop-symbolic" if loading else "view-refresh-symbolic")
        self.reload.set_tooltip_text("Stop loading" if loading else "Reload (F5 or Ctrl+R)")

    def _load_changed(self, view, event, tab):
        # A failed load still finishes, and so does the error page shown for
        # it; the failure stays reported until a different address starts.
        if event == WebKit.LoadEvent.STARTED and view.get_uri() != tab.get("failed_uri"):
            tab["failed_uri"] = None
        showing_error = tab.get("failed_uri") is not None
        if event == WebKit.LoadEvent.FINISHED:
            self.progress.set_visible(False)
            if not showing_error:
                tab["loaded"] = True
                self.status.set_text("Loaded: %s" % (view.get_title() or self._tab_uri(tab)))
        elif event == WebKit.LoadEvent.STARTED:
            tab["loaded"] = False
            if not showing_error:
                self.status.set_text("Loading…")
        if tab is self._current():
            self._sync_toolbar(tab)

    def _load_failed(self, view, _event, uri, error, tab):
        if error.matches(WebKit.NetworkError.quark(), WebKit.NetworkError.CANCELLED):
            return False
        tab["failed_uri"] = uri
        self.status.set_text("Load failed: %s" % error.message)
        self.progress.set_visible(False)
        view.load_alternate_html(
            "<html><body style='font-family:sans-serif;background:#111;color:#f5f5f5;margin:48px'>"
            "<h1>This page could not be opened</h1><p>%s</p><p>%s</p><p>Check the address or the network "
            "connection, then press Reload.</p></body></html>" % (html.escape(uri), html.escape(error.message)),
            uri, None)
        return True

    def _title_changed(self, view, _pspec, tab):
        tab["label"].set_text(view.get_title() or "New tab")
        # Titles often arrive after the load finishes; show the real one.
        if tab.get("loaded") and view.get_title() and tab is self._current():
            self.status.set_text("Loaded: %s" % view.get_title())

    def _progress_changed(self, view, _pspec, tab):
        if tab is self._current():
            fraction = view.get_estimated_load_progress()
            self.progress.set_visible(fraction < 1.0)
            self.progress.set_fraction(fraction)

    def _go_back(self):
        tab = self._current()
        if tab and tab["view"].can_go_back():
            tab["view"].go_back()

    def _go_forward(self):
        tab = self._current()
        if tab and tab["view"].can_go_forward():
            tab["view"].go_forward()

    def _reload_or_stop(self):
        tab = self._current()
        if not tab:
            return
        view = tab["view"]
        if hasattr(view, "is_loading") and view.is_loading():
            view.stop_loading()
            self.status.set_text("Stopped")
        else:
            view.reload()

    def _zoom_by(self, step):
        self._zoom = ZOOM_STEPS.index(1.0) if step == 0 else max(0, min(len(ZOOM_STEPS) - 1, self._zoom + step))
        for tab in self._tabs:
            tab["view"].set_zoom_level(ZOOM_STEPS[self._zoom])
        self.status.set_text("Zoom %d%%" % round(ZOOM_STEPS[self._zoom] * 100))

    def _bookmark(self):
        tab = self._current()
        if not tab:
            return
        uri = self._tab_uri(tab)
        if uri == HOME_URI:
            self.status.set_text("Open a page before bookmarking it.")
            return
        if any(b["uri"] == uri for b in self.bookmarks):
            self.status.set_text("Already bookmarked.")
            return
        self.bookmarks.append({"uri": uri, "title": tab["view"].get_title() or uri})
        self._refresh_bookmarks()
        self.status.set_text("Bookmarked: %s" % self.bookmarks[-1]["title"])

    def _refresh_bookmarks(self):
        while (row := self.bookmark_list.get_row_at_index(0)) is not None:
            self.bookmark_list.remove(row)
        if not self.bookmarks:
            empty = Gtk.Label(label="No bookmarks yet. Use the star to add one.")
            empty.set_margin_top(8); empty.set_margin_bottom(8)
            self.bookmark_list.append(empty)
        for bookmark in self.bookmarks:
            row = Gtk.ListBoxRow(); row.uri = bookmark["uri"]
            row.set_child(Gtk.Label(label=bookmark["title"], xalign=0, max_width_chars=40, ellipsize=3))
            row.set_tooltip_text(bookmark["uri"])
            row.update_property([Gtk.AccessibleProperty.LABEL], [bookmark["title"]])
            self.bookmark_list.append(row)

    def _bookmark_opened(self, _list, row):
        uri = getattr(row, "uri", None)
        if uri:
            self.bookmark_menu.popdown()
            self.url.set_text(uri)
            self._load(None)

    def _download_started(self, _session, download):
        downloads = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOWNLOAD) or os.path.expanduser("~/Downloads")
        download.connect("decide-destination", self._decide_destination, downloads)
        download.connect("finished", lambda d: self.status.set_text("Downloaded to %s" % (d.get_destination() or downloads)))
        download.connect("failed", lambda _d, error: self.status.set_text("Download failed: %s" % error.message))

    def _decide_destination(self, download, suggested, downloads):
        os.makedirs(downloads, exist_ok=True)
        name = os.path.basename(suggested or "download") or "download"
        target, stem, n = os.path.join(downloads, name), os.path.splitext(name), 1
        while os.path.exists(target):
            target = os.path.join(downloads, "%s (%d)%s" % (stem[0], n, stem[1])); n += 1
        download.set_destination(target)
        self.status.set_text("Downloading %s…" % os.path.basename(target))
        return True

    # -- loading ---------------------------------------------------------

    def _load(self, widget):
        address = normalize_address(self.url.get_text())
        if not address: return
        self.url.set_text(address)
        if self.backend == "webkit":
            tab = self._current() or self._add_tab()
            if tab:
                tab["view"].load_uri(address)
            return
        self.status.set_text("Loading…")
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

    # -- Journal ---------------------------------------------------------

    def write_file(self, file_path):
        if self.backend == "webkit":
            tabs = []
            for t in self._tabs:
                uri = self._tab_uri(t)
                # The welcome page's title depends on load timing; save none.
                tabs.append({"uri": uri, "title": "" if uri == HOME_URI else t["label"].get_text()})
            current = self._tabs.index(self._current()) if self._current() in self._tabs else 0
        else:
            address = self.url.get_text().strip()
            tabs = [{"uri": address or HOME_URI, "title": address or "New tab"}]
            current = 0
        state = {"version": FORMAT_VERSION, "tabs": tabs, "current": current, "bookmarks": self.bookmarks}
        Path(file_path).write_text(json.dumps(state, sort_keys=True) + "\n", encoding="utf-8")

    def read_file(self, file_path):
        """Reopen saved tabs and bookmarks."""
        try:
            state = json.loads(Path(file_path).read_text(encoding="utf-8"))
            if not isinstance(state, dict):
                raise ValueError("state must be an object")
        except (OSError, ValueError, TypeError):
            return
        tabs = [t for t in state.get("tabs", []) if isinstance(t, dict) and isinstance(t.get("uri"), str)] \
            if isinstance(state.get("tabs"), list) else []
        bookmarks = state.get("bookmarks") if isinstance(state.get("bookmarks"), list) else []
        self.bookmarks = [{"uri": b["uri"], "title": str(b.get("title") or b["uri"])} for b in bookmarks
                          if isinstance(b, dict) and isinstance(b.get("uri"), str)]
        if self.backend == "webkit":
            self._refresh_bookmarks()
            if tabs:
                for tab in list(self._tabs):
                    tab["view"].stop_loading()
                    self.notebook.remove_page(self.notebook.page_num(tab["view"]))
                self._tabs = []
                for saved in tabs[:MAX_TABS]:
                    self._add_tab(saved["uri"], str(saved.get("title") or "") or None)
                current = state.get("current", 0)
                if isinstance(current, int) and 0 <= current < len(self._tabs):
                    self.notebook.set_current_page(current)
        elif tabs and tabs[0]["uri"] != HOME_URI:
            self.url.set_text(tabs[0]["uri"])
