#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017, Cristian García <cristian99garcia@gmail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

from center_box import CenterBox
from constants import ResultBallType
from ball_box import ResultBallBox

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import Gdk


class ResultBox(CenterBox):

    def __init__(self, columns=4):
        CenterBox.__init__(self)

        self.columns = columns
        self.set_border_width(2)

        self.grid = Gtk.Grid()
        self.grid.set_size_request(16 * columns, 1)
        self.set_center_child(self.grid)

        self.show_all()

    def set_data(self, correct, user):
        balls = []

        for x in range(0, len(correct)):
            if correct[x] == user[x]:
                balls.append(ResultBallType.BLACK)

        for x in range(0, len(correct)):
            if correct[x] in user and correct[x] != user[x]:
                balls.append(ResultBallType.WHITE)

        x = 0
        for ballid in balls:
            box = ResultBallBox.new_from_id(ballid)
            self.grid.attach(box, x, 0, 1, 1)

            x += 1

        self.show_all()
