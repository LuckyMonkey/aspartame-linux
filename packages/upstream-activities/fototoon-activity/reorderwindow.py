import cairo
from gettext import gettext as _

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GdkPixbuf

from sugar3.graphics import style
from sugar3.graphics.toolbutton import ToolButton

HANDLE_SIZE = 18
MIN_IMAGE_SIZE = 50


class BaseWindow(Gtk.Window):

    def __init__(self, width=-1, height=-1):
        GObject.GObject.__init__(self)
        self.set_border_width(style.LINE_WIDTH)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_decorated(False)
        self.set_resizable(False)
        if width == -1:
            width = Gdk.Screen.width() - style.GRID_CELL_SIZE * 2
        if height == -1:
            height = Gdk.Screen.height() - style.GRID_CELL_SIZE * 2
        self.set_size_request(width, height)


class BasicToolbar(Gtk.Toolbar):

    def __init__(self, icon_name, title=''):
        GObject.GObject.__init__(self)

        icon = ToolButton(icon_name)
        self.insert(icon, -1)

        label = Gtk.Label()
        label.set_markup('<b>%s</b>' % title)
        label.set_alignment(0, 0.5)
        tool_item = Gtk.ToolItem()
        tool_item.set_expand(True)
        tool_item.add(label)
        tool_item.show_all()
        self.insert(tool_item, -1)

        self.separator = Gtk.SeparatorToolItem()
        self.separator.props.draw = False
        self.separator.set_expand(True)
        self.insert(self.separator, -1)

        self.stop = ToolButton(icon_name='dialog-cancel')
        self.stop.set_tooltip(_('Cancel'))
        self.insert(self.stop, -1)
        self.stop.show()

        self.confirm = ToolButton(icon_name='dialog-ok')
        self.confirm.set_tooltip(_('Done'))
        self.insert(self.confirm, -1)
        self.confirm.show()


class ReorderView(BaseWindow):

    def __init__(self, activity):
        BaseWindow.__init__(self)
        self.toolbar = BasicToolbar('thumbs-view')

        self.toolbar.stop.connect('clicked', self.__stop_clicked_cb)
        self.toolbar.confirm.connect('clicked', self.__ok_clicked_cb)

        self.scrollwin = ReorderObjects(activity)
        title = _('Drag the images to reorder')
        label = Gtk.Label('')
        label.set_markup('<span size="x-large">%s</span>' % title)
        self.vbox = Gtk.VBox()
        self.vbox.pack_start(self.toolbar, False, False, 0)
        self.vbox.pack_start(label, False, False, style.DEFAULT_SPACING)
        self.vbox.pack_start(self.scrollwin, True, True, 0)
        self.add(self.vbox)
        self.scrollwin.show()
        self.modify_bg(Gtk.StateType.NORMAL,
                       style.COLOR_WHITE.get_gdk_color())

    def __stop_clicked_cb(self, button):
        self.destroy()

    def __ok_clicked_cb(self, button):
        self.scrollwin.reorder_comicboxs()
        self.scrollwin.display_comicboxs()
        self.destroy()


class ReorderObjects(Gtk.ScrolledWindow):
    def __init__(self, activity):
        GObject.GObject.__init__(self)
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
        self.activity = activity
        self.comicboxes = self.activity.page.boxs

        self.liststore = Gtk.ListStore(GdkPixbuf.Pixbuf)
        self.iconview = Gtk.IconView.new()
        self.iconview.set_property('item-width', 200)
        self.iconview.set_model(self.liststore)
        self.iconview.set_pixbuf_column(0)
        self.iconview.set_reorderable(True)

        for comicbox in self.comicboxes[1:]:
            self.liststore.append([comicbox.get_thumbnail()])

        self.add(self.iconview)

    def on_item_activated(self):
        model = self.iconview.get_model()
        pixbuf = model[self.iconview.get_selected_items()[0]][0]
        for comicbox in self.comicboxes[1:]:
            if pixbuf is comicbox.thumbnail:
                self.editor = ImageEditorView(comicbox)
                self.editor.show_all()
                break

    def reorder_comicboxs(self):
        sorted_list = []
        for row in self.liststore:
            for comicbox in self.comicboxes[1:]:
                if row[0] is comicbox.thumbnail:
                    self.activity.page.table.remove(comicbox)
                    sorted_list.append(comicbox)
                    break
        sorted_list.insert(0, self.comicboxes[0])
        self.comicboxes = sorted_list
        self.activity.page.boxs = self.comicboxes

    def display_comicboxs(self):
        for i in range(0, len(self.comicboxes[1:])):
            reng = int(i / 2)
            column = i - (reng * 2)
            self.activity.page.table.attach(
                self.comicboxes[i + 1], column, column + 1, reng, reng + 1)


class ImageElement:
    def __init__(self, pixbuf, box, x, y, w, h):
        self.box = box
        self.pixbuf = pixbuf
        self.pixbuf_original = self.pixbuf.scale_simple(
            self.pixbuf.get_width(), self.pixbuf.get_height(),
            GdkPixbuf.InterpType.BILINEAR)
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.calculate_boundaries()
        self.calculate_points()
        self.margin_x = 0
        self.margin_y = 0
        self.box_width = 0
        self.box_height = 0

    def reset(self):
        self.x = 0
        self.y = 0
        self.width = self.box_width
        self.height = self.box_height
        self.calculate_boundaries()
        self.calculate_points()

    def calculate_boundaries(self):
        self.boundaries = {}
        self.boundaries['min_x'] = self.x
        self.boundaries['max_x'] = self.x + self.width
        self.boundaries['min_y'] = self.y
        self.boundaries['max_y'] = self.y + self.height

    def calculate_points(self):
        self.points = {}
        self.points["upper_left"] = [self.x, self.y]
        self.points["upper_right"] = [self.x + self.width - HANDLE_SIZE,
                                      self.y]
        self.points["lower_left"] = [self.x,
                                     self.y + self.height - HANDLE_SIZE]
        self.points["lower_right"] = [self.x + self.width - HANDLE_SIZE,
                                      self.y + self.height - HANDLE_SIZE]

    def is_selected(self, x, y):
        # substract the margin values
        x = x - self.margin_x
        y = y - self.margin_y

        if (x >= self.boundaries['min_x'] and
            x <= self.boundaries['max_x']) and \
           (y >= self.boundaries['min_y'] and
                y <= self.boundaries['max_y']):
            return True
        else:
            return False

    def is_resize(self, x, y):
        if self.is_in_point(x, y):
            return True
        else:
            return False

    def is_in_point(self, x, y, point=None):
        if point is not None:
            # substract the margin values
            x = x - self.margin_x
            y = y - self.margin_y

            if (x >= point[0] and x <= (point[0] + HANDLE_SIZE)) \
                    and (y >= point[1] and y <= (point[1] + HANDLE_SIZE)):
                return True
            else:
                return False
        else:
            if self.is_in_point(x, y, self.points["upper_left"]) or \
                self.is_in_point(x, y, self.points["upper_right"]) or \
                self.is_in_point(x, y, self.points["lower_left"]) or \
                    self.is_in_point(x, y, self.points["lower_right"]):
                return True
            else:
                return False

    def draw(self, ctx):
        self.image = ctx.get_target().create_similar(
            cairo.CONTENT_COLOR_ALPHA, self.box.width,
            self.box.height)
        pixb_scaled = self.pixbuf_original.scale_simple(
            self.width, self.height, GdkPixbuf.InterpType.BILINEAR)
        ct = cairo.Context(self.image)
        Gdk.cairo_set_source_pixbuf(ct, pixb_scaled, self.x, self.y)
        ct.paint()
        self.pixbuf = pixb_scaled

        ctx.save()
        ctx.translate(self.margin_x, self.margin_y)
        ctx.rectangle(0, 0, self.box.width, self.box.height)
        ctx.clip()
        ctx.set_source_surface(self.image, 0, 0)
        ctx.paint()
        ctx.restore()

        # draw the box border
        ctx.save()
        ctx.rectangle(self.margin_x, self.margin_y, self.box_width,
                      self.box_height)
        ctx.set_source_rgb(0, 0, 0)
        ctx.stroke()
        ctx.restore()

        # draw the image border
        ctx.save()
        ctx.translate(self.margin_x, self.margin_y)
        ctx.set_line_width(2)
        ctx.set_source_rgb(1, 1, 1)
        ctx.rectangle(self.x, self.y, self.width, self.height)
        ctx.stroke_preserve()
        ctx.set_source_rgb(0, 0, 0)
        ctx.set_dash([2])
        ctx.stroke()
        ctx.restore()

        # draw hadles
        self._draw_handle(ctx, self.x, self.y)
        self._draw_handle(ctx, self.x + self.width - HANDLE_SIZE, self.y)
        self._draw_handle(ctx, self.x, self.y + self.height - HANDLE_SIZE)
        self._draw_handle(ctx, self.x + self.width - HANDLE_SIZE,
                          self.y + self.height - HANDLE_SIZE)

    def _draw_handle(self, ctx, x, y):
        ctx.save()
        ctx.translate(self.margin_x, self.margin_y)
        ctx.set_line_width(2)
        ctx.set_source_rgb(1, 1, 1)
        ctx.rectangle(x, y, HANDLE_SIZE, HANDLE_SIZE)
        ctx.stroke_preserve()
        ctx.set_source_rgb(0, 0, 0)
        ctx.set_dash([2])
        ctx.stroke()
        ctx.restore()

    def move(self, x_movement, y_movement, allocation):
        self.x = self.x + x_movement
        self.y = self.y + y_movement
        if self.x + self.width > allocation.width:
            self.x -= (self.x + self.width) - (allocation.width)

        if self.y + self.height > allocation.height:
            self.y -= (self.y + self.height) - (allocation.height)

        self.calculate_boundaries()
        self.calculate_points()

    def resize(self, x_movement, y_movement, allocation, start_x, start_y):

        if self.is_in_point(start_x, start_y, self.points["lower_left"]):
            self.x += x_movement
            self.width -= x_movement
            self.height += y_movement
        elif self.is_in_point(start_x, start_y, self.points["upper_right"]):
            self.y += y_movement
            self.height -= y_movement
            self.width += x_movement
        elif self.is_in_point(start_x, start_y, self.points["upper_left"]):
            self.y += y_movement
            self.x += x_movement
            self.width -= x_movement
            self.height -= y_movement
        else:
            self.height += y_movement
            self.width += x_movement

        if self.width < MIN_IMAGE_SIZE:
            self.width = MIN_IMAGE_SIZE
        if self.height < MIN_IMAGE_SIZE:
            self.height = MIN_IMAGE_SIZE

        if self.x + self.width > allocation.width:
            self.width -= (self.x + self.width) - (allocation.width)

        if self.y + self.height > allocation.height:
            self.height -= (self.y + self.height) - (allocation.height)

        self.calculate_boundaries()
        self.calculate_points()


class CanvasEditor(Gtk.EventBox):
    def __init__(self, comicbox, width, height, window):
        Gtk.EventBox.__init__(self)

        self.width = width
        self.height = height
        self.is_resize = False
        self.is_move = False
        self.parentw = window

        self.modify_bg(Gtk.StateType.NORMAL,
                       style.COLOR_WHITE.get_gdk_color())
        self._drawingarea = Gtk.DrawingArea()
        self.add(self._drawingarea)

        self._drawingarea.add_events(
            Gdk.EventMask.POINTER_MOTION_MASK |
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.BUTTON_RELEASE_MASK |
            Gdk.EventMask.BUTTON_MOTION_MASK)

        self.image = ImageElement(
            comicbox.pixbuf, self,
            comicbox.img_x, comicbox.img_y,
            comicbox.img_w, comicbox.img_h)

        self._drawingarea.connect("draw", self.draw_cb)
        self.connect("button_press_event", self.pressing)
        self.connect("motion_notify_event", self.mouse_move)
        self.connect("motion_notify_event", self.moving)
        self.connect("button_release_event", self.releassing)
        self.redraw()

        def size_allocate(widget, allocation):
            self._drawingarea.set_size_request(allocation.width,
                                               allocation.height)
            self.image.margin_x = (allocation.width - self.width) // 2
            self.image.margin_y = (allocation.height - self.height) // 2
            self.image.box_width = self.width
            self.image.box_height = self.height

        self.connect('size_allocate', size_allocate)
        self.set_size_request(self.width, self.height)
        self._drawingarea.set_size_request(self.width, self.height)
        self.show_all()

    def redraw(self):
        self._drawingarea.queue_draw()

    def draw_cb(self, widget, context):
        self.image.draw(context)

    def pressing(self, widget, event):
        if self.image.is_selected(event.x, event.y):
            if self.image.is_in_point(event.x, event.y):
                self.is_resize = True
                self.is_move = False
            else:
                self.is_resize = False
                self.is_move = True
        self.start_x = event.x
        self.start_y = event.y

    def mouse_move(self, widget, event):
        cursor = None
        if self.image.is_in_point(event.x, event.y,
                                  self.image.points["upper_left"]) or \
            self.image.is_in_point(event.x, event.y,
                                   self.image.points["lower_right"]):
            cursor = Gdk.Cursor(Gdk.CursorType.BOTTOM_RIGHT_CORNER)
        elif self.image.is_in_point(event.x, event.y,
                                    self.image.points["upper_right"]) or \
            self.image.is_in_point(event.x, event.y,
                                   self.image.points["lower_left"]):
            cursor = Gdk.Cursor(Gdk.CursorType.BOTTOM_LEFT_CORNER)
        elif self.image.is_selected(event.x, event.y):
            cursor = Gdk.Cursor(Gdk.CursorType.FLEUR)
        self.get_window().set_cursor(cursor)

    def moving(self, widget, event):
        if self.is_move:
            x_movement = event.x - self.start_x
            y_movement = event.y - self.start_y
            self.image.move(x_movement, y_movement, self.get_allocation())
            self.start_x = event.x
            self.start_y = event.y
            self.redraw()
        elif self.is_resize:
            x_movement = event.x - self.start_x
            y_movement = event.y - self.start_y
            self.image.resize(x_movement, y_movement, self.get_allocation(),
                              self.start_x, self.start_y)
            self.start_x = event.x
            self.start_y = event.y
            self.redraw()

    def releassing(self, widget, event):
        self.is_resize = False
        self.is_move = False
        self.start_x = -1
        self.start_y = -1

    def reset(self):
        self.image.reset()
        self.redraw()


class ImageEditorView(BaseWindow):

    def __init__(self, comicbox):
        BaseWindow.__init__(self)

        self.toolbar = BasicToolbar('contract-coordinates')
        self.toolbar.stop.connect('clicked', self.__stop_clicked_cb)
        self.toolbar.confirm.connect('clicked', self.__ok_clicked_cb)

        reset_size = ToolButton(icon_name='box-size')
        reset_size.set_tooltip(_('Reset to box size'))
        self.toolbar.insert(reset_size, 3)
        reset_size.show()
        reset_size.connect('clicked', self.__reset_size_cb)

        self.comicbox = comicbox
        self.canvas = CanvasEditor(
            self.comicbox, self.comicbox.width,
            self.comicbox.height, self)

        label = Gtk.Label('')
        title = _('Drag to move or resize using the marked corners')
        label.set_markup('<span size="x-large">%s</span>' % title)

        self.vbox = Gtk.VBox()
        self.vbox.pack_start(self.toolbar, False, False, 0)
        self.vbox.pack_start(label, False, False, style.DEFAULT_SPACING)
        self.vbox.pack_start(self.canvas, True, True, 0)
        self.add(self.vbox)
        self.modify_bg(Gtk.StateType.NORMAL,
                       style.COLOR_WHITE.get_gdk_color())

    def __reset_size_cb(self, button):
        self.canvas.reset()

    def __stop_clicked_cb(self, button):
        self.destroy()

    def __ok_clicked_cb(self, button):
        self.comicbox.img_x = self.canvas.image.x
        self.comicbox.img_y = self.canvas.image.y
        self.comicbox.img_w = self.canvas.image.width
        self.comicbox.img_h = self.canvas.image.height
        self.comicbox.redraw()
        self.destroy()
