"""GTK4-native Poll Activity with a local, readable voting model."""

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class PollActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Poll")
        self.votes = [0, 0, 0]
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        root.set_margin_top(28); root.set_margin_bottom(28)
        root.set_margin_start(32); root.set_margin_end(32)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Poll"])
        root.set_accessible_role(Gtk.AccessibleRole.GROUP)
        title = Gtk.Label(label="Poll", xalign=0); title.add_css_class("title-1"); root.append(title)
        self.question = Gtk.Entry(); self.question.set_text("What should we explore today?")
        self.question.set_placeholder_text("Type a question"); self.question.update_property([Gtk.AccessibleProperty.LABEL], ["Poll question"])
        root.append(self.question)
        self.options = []
        for index, text in enumerate(("Create", "Discover", "Share")):
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            entry = Gtk.Entry(); entry.set_text(text); entry.set_hexpand(True); entry.update_property([Gtk.AccessibleProperty.LABEL], ["Choice %d" % (index + 1)])
            button = Gtk.Button(label="Vote"); button.connect("clicked", self._vote, index)
            count = Gtk.Label(label="0 votes", xalign=0); count.set_width_chars(10)
            row.append(entry); row.append(button); row.append(count); root.append(row)
            self.options.append((entry, count))
        self.status = Gtk.Label(label="Choose an option to cast your vote.", xalign=0); self.status.set_opacity(.8); root.append(self.status)
        reset = Gtk.Button(label="Reset votes"); reset.connect("clicked", self._reset); root.append(reset)
        self.set_canvas(root); self._install_css()

    def _install_css(self):
        provider = Gtk.CssProvider(); provider.load_from_data(b"button { min-height: 38px; border-radius: 18px; } entry { min-height: 38px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _vote(self, _button, index):
        self.votes[index] += 1
        self.options[index][1].set_text("%d vote%s" % (self.votes[index], "" if self.votes[index] == 1 else "s"))
        self.status.set_text("Vote recorded for %s." % self.options[index][0].get_text())

    def _reset(self, _button):
        self.votes = [0, 0, 0]
        for _entry, count in self.options: count.set_text("0 votes")
        self.status.set_text("Votes reset.")

