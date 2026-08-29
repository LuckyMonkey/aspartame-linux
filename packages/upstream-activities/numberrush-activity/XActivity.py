#
# Copyright (C) 2018 Azhar Ali Khaked <gr33nmayhem@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import pygame

from sugar3.activity.activity import Activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.activity.widgets import StopButton


sys.path.append('..')  # Import sugargame package from top directory.
import sugargame.canvas

import NumRush


class XActivity(Activity):
    def __init__(self, handle):
        Activity.__init__(self, handle)

        # Create the game instance.
        self.game = NumRush.numrush()

        # Build the activity toolbar.
        self.build_toolbar()

        if 'score' in self.metadata:
            self._restore()

        # Build the Pygame canvas and start the game running
        # (self.game.run is called when the activity constructor
        # returns).
        self._pygamecanvas = sugargame.canvas.PygameCanvas(self,
            main=self.game.run, modules=[pygame.display, pygame.font])

        # Note that set_canvas implicitly calls read_file when
        # resuming from the Journal.
        self.set_canvas(self._pygamecanvas)
        self._pygamecanvas.grab_focus()

    def build_toolbar(self):
        toolbar_box = ToolbarBox()
        self.set_toolbar_box(toolbar_box)
        toolbar_box.show()

        activity_button = ActivityToolbarButton(self)
        toolbar_box.toolbar.insert(activity_button, -1)
        activity_button.show()

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()

        stop_button = StopButton(self)
        toolbar_box.toolbar.insert(stop_button, -1)
        stop_button.show()
        stop_button.connect('clicked', self._stop_cb)

    def _stop_cb(self, button):
        self.game.running = False

    def read_file(self, file_path):
        pass  # self.game.read_file(file_path)

    def write_file(self, file_path):
        hscore, score, n, randomOptions, strin = self.game.save_game()
        self.metadata['hscore'] = str(hscore)
        self.metadata['score'] = str(score)
        self.metadata['n'] = str(n)
        self.metadata['randomOptions'] = str(randomOptions)
        self.metadata['strin'] = strin

    def _restore(self):
        """ Restore the game state from metadata """
        self._restoring = True
        if 'hscore' in self.metadata:
            hscore = int(self.metadata['hscore'])
        else:
            hscore = 0
        if 'score' in self.metadata:
            score = int(self.metadata['score'])
        else:
            score = 0
        if 'n' in self.metadata:
            n = int(self.metadata['n'])
        else:
            score = 0
        if 'randomOptions' in self.metadata:
            randomOptions = self.metadata['randomOptions'][1:-1].split(",")
            randomOptions = list(map(int, randomOptions))
        else:
            randomOptions = [0, 0, 0]
        if 'strin' in self.metadata:
            strin = self.metadata['strin']
        else:
            strin = '0 - 0'
        self.game.restore_game(hscore, score, n, randomOptions, strin)
        self._restoring = False
