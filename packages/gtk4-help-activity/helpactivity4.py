"""Readable, native GTK4 Help Activity for the modern Sugar Space."""

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class HelpActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Sugar Help")
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        root.add_css_class("help-root")
        root.set_margin_start(32)
        root.set_margin_end(32)
        root.set_margin_top(24)
        root.set_margin_bottom(24)
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
        input_status = Gtk.Label(label="Type to search these topics")
        input_status.set_halign(Gtk.Align.START)
        input_status.add_css_class("dim-label")
        root.append(input_status)

        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        topics = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        scroll.set_child(topics)
        root.append(scroll)
        self.set_canvas(root)
        search.grab_focus()

        sections = (
            ("How Sugar is organized", "Sugar is a focused learning environment built around Home, Activities, the Frame, and the Journal. Each view has one clear purpose and can be reached without leaving your work."),
            ("Home and Activities", "Home shows your Favorites and installed Activities. Select an icon to start or resume it. An Activity is a focused workspace; use the Frame to switch between running Activities. The stop control closes the current Activity and returns its icon to the stopped state."),
            ("Journal", "The Journal saves work as objects rather than a traditional file tree. Search by title or Activity, inspect metadata, resume an entry, or open it in its associated Activity. Use Projects to show entries assigned to a project, and edit a title or project directly in its row. Stopping an Activity does not delete its Journal entries."),
            ("Frame and navigation", "Reveal the Frame from an edge or with the Frame action to see running Activities and system controls. F1 opens Neighborhood, F2 Group, F3 Home, F4 the current Activity, F5 Journal, and F6 Frame. Escape closes a panel or returns to the previous surface."),
            ("Neighborhood and collaboration", "Neighborhood shows nearby people and shared Activities when collaboration services are available. An empty view means no peers are currently visible; it is not an error."),
            ("Count Activity", "Count is a layered grid for building and measuring groups of cells. Click a cell or drag across a rectangle to fill it. New and copied layers appear as translucent context behind or in front of the selected plane; only the highlighted plane is editable. Use the single Delete layer control to remove the selected layer, then save the Activity to keep its layers in the Journal."),
            ("Calculate Activity", "Calculate evaluates basic arithmetic without leaving Sugar. Type an expression such as 2 + 3 * 4, press Enter, or use the keypad buttons. Clear starts a new calculation; invalid or unsupported expressions are reported without executing arbitrary code."),
            ("Clock and JAMClock", "Clock and JAMClock are lightweight time Activities. They show the current time and date and refresh once each second. JAMClock keeps its original Sugar bundle identity while using the native GTK4 implementation in the modern Space; stopping either Activity returns immediately to Home."),
            ("Image Viewer Activity", "Image Viewer opens pictures from the Journal and supports zooming, rotation, and browsing images. Use the Activity toolbar for view controls; closing the Activity returns to Home without changing the original image."),
            ("Terminal and Browse Activities", "Terminal provides a native GTK4 shell inside Sugar and keeps its text input in the Activity surface. Browse provides a native GTK4 web-address and loading surface; full embedded-browser parity remains in progress. Both are isolated Activities: use the Frame to switch away, and use the Activity stop control to end them and return to Home."),
            ("How Activity surfaces work", "The GTK4 shell owns the Sugar window and Casilda provides each Activity with a private Wayland surface. Activity processes receive their own input and lifecycle state; stopping one removes its surface and clears its running icon without stopping the shell."),
            ("Keyboard and accessibility", "Tab and Shift+Tab move focus. Enter or Space activates the focused control. Escape backs out of a panel. Every important control exposes a readable name so keyboard and assistive technology users can follow the same Sugar workflow."),
            ("Further reading", "Learn by trying one Activity, saving an entry to the Journal, stopping it, and resuming it from the Journal. Then compare Favorites, List, Frame, and Neighborhood views to see how Sugar keeps context visible."),
        )
        expanders = []
        for heading, text in sections:
            expander = Gtk.Expander(label=heading)
            expander.set_expanded(heading == "How Sugar is organized")
            expander.update_property([Gtk.AccessibleProperty.LABEL], [heading])
            label = Gtk.Label(label=text, xalign=0)
            label.set_wrap(True)
            label.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
            label.set_selectable(True)
            label.set_margin_start(12)
            label.set_margin_end(12)
            label.set_margin_top(8)
            label.set_margin_bottom(8)
            expander.set_child(label)
            topics.append(expander)
            expanders.append((expander, heading, text))

        def _search_changed(entry):
            query = entry.get_text().strip().casefold()
            visible = 0
            for expander, heading, text in expanders:
                match = not query or query in heading.casefold() or query in text.casefold()
                expander.set_visible(match)
                visible += int(match)
            input_status.set_text(
                f"{visible} topic{'s' if visible != 1 else ''} match"
                if query else "Type to search these topics"
            )

        search.connect("changed", _search_changed)

        provider = Gtk.CssProvider()
        provider.load_from_data(
            b".help-root, .help-root scrolledwindow, .help-root viewport { background-color: #111111; color: #f5f5f5; }"
            b".help-root label { color: #f5f5f5; }"
            b".help-root expander { color: #f5f5f5; border-bottom: 1px solid #444444; padding: 6px; }"
            b".help-root expander title { color: #f5f5f5; font-weight: bold; }"
            b".help-root entry { color: #111111; background-color: #ffffff; }"
        )
        display = Gdk.Display.get_default()
        if display is not None:
            Gtk.StyleContext.add_provider_for_display(
                display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
