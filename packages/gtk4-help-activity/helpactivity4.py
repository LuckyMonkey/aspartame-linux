"""Small native GTK4 Help Activity for the modern Sugar Space."""

from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class HelpActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Sugar Help")
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        root.add_css_class("help-root")
        root.set_margin_start(32)
        root.set_margin_end(32)
        root.set_margin_top(28)
        root.set_margin_bottom(28)
        title = Gtk.Label(label="Sugar Help")
        title.add_css_class("title-1")
        title.set_halign(Gtk.Align.START)
        root.append(title)
        search = Gtk.Entry()
        search.set_placeholder_text("Search help")
        search.set_hexpand(True)
        search.update_property(
            [Gtk.AccessibleProperty.LABEL], ["Search help"]
        )
        root.append(search)
        input_status = Gtk.Label(label="Keyboard ready")
        input_status.set_halign(Gtk.Align.START)
        input_status.add_css_class("dim-label")
        root.append(input_status)

        def _search_changed(entry):
            value = entry.get_text()
            input_status.set_text(
                f"Input received: {value}" if value else "Keyboard ready"
            )

        search.connect("changed", _search_changed)
        body = Gtk.TextView()
        body.set_editable(False)
        body.set_cursor_visible(False)
        body.set_wrap_mode(Gtk.WrapMode.WORD)
        body.get_buffer().set_text(
            "Sugar is organized around Home, Activities, the Frame, and the Journal.\n\n"
            "Home: choose Favorites or List view, search installed Activities, and open an Activity.\n\n"
            "Activities: each Activity is a focused workspace. Use the Frame to switch between running Activities;\n"
            "the stop control closes the current Activity and returns its icon to the stopped state.\n\n"
            "Journal: work is saved as objects. Search, resume, and open entries without navigating a traditional file tree.\n\n"
            "Neighborhood: nearby people and shared Activities appear when collaboration services are available.\n\n"
            "Keyboard: F1 Neighborhood, F2 Group, F3 Home, F4 Activity, F5 Journal, and F6 Frame.\n"
            "Escape closes the current panel or returns to the previous shell surface."
        )
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_child(body)
        root.append(scroll)
        self.set_canvas(root)
        search.grab_focus()

        provider = Gtk.CssProvider()
        provider.load_from_data(
            b".help-root { background-color: #111111; color: #f5f5f5; }"
            b".help-root label { color: #f5f5f5; }"
            b".help-root textview { color: #f5f5f5; background-color: #111111; }"
            b".help-root entry { color: #111111; background-color: #ffffff; }"
        )
        display = Gdk.Display.get_default()
        if display is not None:
            Gtk.StyleContext.add_provider_for_display(
                display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
