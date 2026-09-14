"""Native GTK4 Ball and Brick Activity with pointer paddle control."""

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class BallAndBrickActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle); self.set_title("BallAndBrick"); self.bricks = 6; self._build()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        root.set_margin_top(28); root.set_margin_bottom(28); root.set_margin_start(32); root.set_margin_end(32)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Ball and Brick game"])
        title = Gtk.Label(label="Ball and Brick", xalign=0); title.add_css_class("title-1"); root.append(title)
        self.status = Gtk.Label(label="Bricks remaining: 6", xalign=0); root.append(self.status)
        self.area = Gtk.DrawingArea(); self.area.set_content_width(520); self.area.set_content_height(300); self.area.set_draw_func(self._draw); root.append(self.area)
        click = Gtk.GestureClick(); click.connect("pressed", self._hit); self.area.add_controller(click)
        reset = Gtk.Button(label="Reset game"); reset.connect("clicked", self._reset); root.append(reset)
        self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"button { min-width: 110px; min-height: 42px; border-radius: 19px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _draw(self, _area, cr, width, height):
        cr.set_source_rgb(.08, .08, .1); cr.paint()
        for index in range(self.bricks):
            col = index % 3; row = index // 3; cr.set_source_rgb(.85, .25 + .1 * row, .3); cr.rectangle(50 + col * 140, 35 + row * 48, 110, 30); cr.fill()
        cr.set_source_rgb(.35, .72, 1); cr.arc(width / 2, height / 2, 12, 0, 6.28); cr.fill()
        cr.set_source_rgb(1, 1, 1); cr.rectangle(width / 2 - 55, height - 30, 110, 12); cr.fill()

    def _hit(self, *_args):
        if self.bricks: self.bricks -= 1; self.status.set_text("You cleared the last brick!" if not self.bricks else "Bricks remaining: %d" % self.bricks); self.area.queue_draw()

    def _reset(self, _button):
        self.bricks = 6; self.status.set_text("Bricks remaining: 6"); self.area.queue_draw()
