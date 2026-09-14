"""Native GTK4 FotoToon caption canvas Activity."""

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class FotoToonActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("FotoToon"); self.caption = ""; self._build()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        root.set_margin_top(28); root.set_margin_bottom(28); root.set_margin_start(32); root.set_margin_end(32)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["FotoToon canvas"])
        title = Gtk.Label(label="FotoToon", xalign=0); title.add_css_class("title-1"); root.append(title)
        self.canvas = Gtk.DrawingArea(); self.canvas.set_content_width(560); self.canvas.set_content_height(320); self.canvas.set_draw_func(self._draw); root.append(self.canvas)
        click = Gtk.GestureClick(); click.connect("pressed", self._stamp); self.canvas.add_controller(click)
        self.entry = Gtk.Entry(); self.entry.set_placeholder_text("Caption"); self.entry.update_property([Gtk.AccessibleProperty.LABEL], ["Caption text"]); self.entry.connect("changed", self._caption); root.append(self.entry)
        self.status = Gtk.Label(label="Click the canvas to place a panel.", xalign=0); self.status.add_css_class("dim-label"); root.append(self.status)
        reset = Gtk.Button(label="Clear canvas"); reset.connect("clicked", self._reset); root.append(reset)
        self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"entry { min-height: 42px; } button { min-height: 42px; border-radius: 19px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _draw(self, _area, cr, width, height):
        cr.set_source_rgb(.12, .12, .14); cr.paint(); cr.set_source_rgb(.25, .6, .8); cr.rectangle(35, 35, width - 70, height - 70); cr.fill(); cr.set_source_rgb(1, 1, 1); cr.select_font_face("Sans"); cr.set_font_size(24); cr.move_to(55, height - 55); cr.show_text(self.caption or "Your caption")

    def _stamp(self, _gesture, _n, _x, _y):
        self.status.set_text("Panel placed — edit the caption below."); self.canvas.queue_draw()

    def _caption(self, entry):
        self.caption = entry.get_text(); self.canvas.queue_draw()

    def _reset(self, _button):
        self.caption = ""; self.entry.set_text(""); self.status.set_text("Click the canvas to place a panel."); self.canvas.queue_draw()
