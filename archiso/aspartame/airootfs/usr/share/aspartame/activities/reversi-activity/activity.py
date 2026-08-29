#! /usr/bin/env python
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
import sugargame
import sugargame.canvas
import pygame
from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.graphics.toolbarbox import ToolbarButton
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.colorbutton import ColorToolButton
from sugar3.activity.widgets import StopButton
from gettext import gettext as _
import reversi


class ReversiActivity(activity.Activity):
    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        self.sound_enable = True
        self.game = reversi.ReversiController(self)
        self.game.canvas = sugargame.canvas.PygameCanvas(
            self,
            main=self.game.run,
            modules=[pygame.display, pygame.font])
        self.set_canvas(self.game.canvas)
        self.game.canvas.grab_focus()
        self.build_toolbar()

    def build_toolbar(self):
        toolbar_box = ToolbarBox()
        self.set_toolbar_box(toolbar_box)
        toolbar_box.show()

        activity_button = ActivityToolbarButton(self)
        toolbar_box.toolbar.insert(activity_button, -1)
        activity_button.show()

        separator = Gtk.SeparatorToolItem()
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()

        self.build_colors_toolbar(toolbar_box)

        separator = Gtk.SeparatorToolItem()
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()

        # new game button
        new_game = ToolButton('new-game')
        new_game.connect('clicked', self._new_game)
        new_game.set_tooltip(_('New game'))
        toolbar_box.toolbar.insert(new_game, -1)

        separator = Gtk.SeparatorToolItem()
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()

        # current
        item = Gtk.ToolItem()
        label = Gtk.Label()
        label.set_text(' %s ' % _('Current player:'))
        item.add(label)
        toolbar_box.toolbar.insert(item, -1)

        # player
        item = Gtk.ToolItem()
        self.current_label = Gtk.Label()
        self.current_label.set_text(' %s' % 1)
        item.add(self.current_label)
        toolbar_box.toolbar.insert(item, -1)

        separator = Gtk.SeparatorToolItem()
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()

        sound_button = ToolButton('speaker-muted-100')
        sound_button.set_tooltip(_('Sound'))
        sound_button.connect('clicked', self.sound_control)
        toolbar_box.toolbar.insert(sound_button, -1)

        # separator and stop
        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()

        stop_button = StopButton(self)
        toolbar_box.toolbar.insert(stop_button, -1)
        stop_button.show()

        self.show_all()

    def build_colors_toolbar(self, toolbox):

        colors_bar = Gtk.Toolbar()

        ######################################################################
        # Point color
        item = Gtk.ToolItem()
        label = Gtk.Label()
        label.set_text('%s ' % _('Player 1'))
        item.add(label)
        colors_bar.insert(item, -1)

        # select color
        item = Gtk.ToolItem()
        _fill_color = ColorToolButton()
        color = Gdk.Color(
            red=65535,
            green=65535,
            blue=65535)
        _fill_color.set_color(color)
        _fill_color.connect('notify::color', self.color_player1_change)
        item.add(_fill_color)
        colors_bar.insert(item, -1)

        # Separator
        separator = Gtk.SeparatorToolItem()
        colors_bar.insert(separator, -1)
        separator.show()

        ######################################################################
        # Back color
        item = Gtk.ToolItem()
        label = Gtk.Label()
        label.set_text('%s ' % _('Player 2'))
        item.add(label)
        colors_bar.insert(item, -1)

        # select color
        item = Gtk.ToolItem()
        _fill_color = ColorToolButton()
        color = Gdk.Color(
            red=0,
            green=0,
            blue=0)
        _fill_color.set_color(color)
        _fill_color.connect('notify::color', self.color_player2_change)
        item.add(_fill_color)
        colors_bar.insert(item, -1)

        # Separator
        separator = Gtk.SeparatorToolItem()
        colors_bar.insert(separator, -1)
        separator.show()

        ######################################################################
        # Line color
        item = Gtk.ToolItem()
        label = Gtk.Label()
        label.set_text('%s ' % _('Lines'))
        item.add(label)
        colors_bar.insert(item, -1)

        # select color
        item = Gtk.ToolItem()
        _fill_color = ColorToolButton()
        _fill_color.connect('notify::color', self.color_line_change)
        item.add(_fill_color)
        colors_bar.insert(item, -1)

        # Separator
        separator = Gtk.SeparatorToolItem()
        colors_bar.insert(separator, -1)
        separator.show()

        ######################################################################
        # Line color
        item = Gtk.ToolItem()
        label = Gtk.Label()
        label.set_text('%s ' % _('Background'))
        item.add(label)
        colors_bar.insert(item, -1)

        # select color
        item = Gtk.ToolItem()
        _fill_color = ColorToolButton()
        color = Gdk.Color(
            red=0,
            green=25700,
            blue=0)
        _fill_color.set_color(color)
        _fill_color.connect('notify::color', self.color_back_change)
        item.add(_fill_color)
        colors_bar.insert(item, -1)

        # Separator
        separator = Gtk.SeparatorToolItem()
        colors_bar.insert(separator, -1)
        separator.show()

        ######################################################################
        # Line color
        item = Gtk.ToolItem()
        label = Gtk.Label()
        label.set_text('%s ' % _('Board'))
        item.add(label)
        colors_bar.insert(item, -1)

        # select color
        item = Gtk.ToolItem()
        _fill_color = ColorToolButton()
        color = Gdk.Color(
            red=0,
            green=0,
            blue=65535)
        _fill_color.set_color(color)
        _fill_color.connect('notify::color', self.color_board_change)
        item.add(_fill_color)
        colors_bar.insert(item, -1)

        ######################################################################
        colors_bar.show_all()
        colors_button = ToolbarButton(label=_('Colors'),
                                      page=colors_bar,
                                      icon_name='toolbar-colors')
        toolbox.toolbar.insert(colors_button, -1)
        colors_button.show()

    def _new_game(self, widget):
        self.game.handle_restart_button_click()

    def color_player1_change(self, widget, pspec):
        color = widget.get_color()
        new_color = self.color_to_rgb(color)
        self.game.set_player1_color(new_color)

    def color_player2_change(self, widget, pspec):
        color = widget.get_color()
        new_color = self.color_to_rgb(color)
        self.game.set_player2_color(new_color)

    def color_line_change(self, widget, pspec):
        color = widget.get_color()
        new_color = self.color_to_rgb(color)
        self.game.set_line_color(new_color)

    def color_back_change(self, widget, pspec):
        color = widget.get_color()
        new_color = self.color_to_rgb(color)
        self.game.set_back_color(new_color)

    def color_board_change(self, widget, pspec):
        color = widget.get_color()
        new_color = self.color_to_rgb(color)
        self.game.set_board_color(new_color)

    def color_to_rgb(self, color):
        r = color.red * 255 / 65535
        g = color.green * 255 / 65535
        b = color.blue * 255 / 65535
        return (r, g, b)

    def set_current_player(self, player):
        self.current_label.set_text(' %s' % player)

    def sound_control(self, button):
        self.sound_enable = not self.sound_enable
        self.game.change_sound(self.sound_enable)
        if not self.sound_enable:
            button.set_icon_name('speaker-muted-000')
            button.set_tooltip(_('No sound'))
        else:
            button.set_icon_name('speaker-muted-100')
            button.set_tooltip(_('Sound'))
