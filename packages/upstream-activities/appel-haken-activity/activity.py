# activity.py
# my standard link between sugar and my activity

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import pygame
from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.activity.widgets import StopButton
import sugargame.canvas
import load_save
import AppelHaken


class PeterActivity(activity.Activity):
    def __init__(self, handle):
        super(PeterActivity, self).__init__(handle)

        # Build the activity toolbar.
        toolbar_box = ToolbarBox()

        activity_button = ActivityToolbarButton(self)
        toolbar_box.toolbar.insert(activity_button, 0)
        activity_button.show()

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = True
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()

        label = Gtk.Label()
        label.set_use_markup(True)
        label.show()
        labelitem = Gtk.ToolItem()
        labelitem.add(label)
        toolbar_box.toolbar.insert(labelitem, -1)
        labelitem.show()

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()

        stop = StopButton(self)
        toolbar_box.toolbar.insert(stop, -1)
        stop.show()

        toolbar_box.show()
        self.set_toolbar_box(toolbar_box)

        # Create the game instance.
        self.game = AppelHaken.AppelHaken()

        # Build the Pygame canvas.
        self.game.canvas = self._pygamecanvas = sugargame.canvas.PygameCanvas(
            self, main=self.game.run, modules=[pygame.display, pygame.font])
        # Note that set_canvas implicitly calls
        # read_file when resuming from the Journal.
        self.set_canvas(self._pygamecanvas)

    def read_file(self, file_path):
        try:
            f = open(file_path, 'r')
        except:
            return
        load_save.load(f)
        f.close()

    def write_file(self, file_path):
        f = open(file_path, 'w')
        load_save.save(f)
        f.close()
