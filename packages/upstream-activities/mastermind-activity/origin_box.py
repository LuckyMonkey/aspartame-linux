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

from ball_box import BallBox
from ball_box import EraserBallBox
from constants import Difficulty
from utils import get_colors_for_difficulty

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject


class OriginBox(Gtk.Grid):

    __gsignals__ = {
        "data-changed": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, []),
    }

    def __init__(self):
        Gtk.Grid.__init__(self)

        self.balls = []
        self.callback_ids = {}
        self.difficulty = None

        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_column_spacing(5)

        self.eraser_ball = EraserBallBox()
        self.attach(self.eraser_ball, 0, 0, 1, 1)

        self.show_all()

    def game_over(self):
        for ball in self.balls:
            ball.set_draggable(False)

    def clear(self):
        while self.balls != []:
            ball = self.balls[0]
            self.balls.remove(ball)
            self.remove(ball)

            del ball

    def reset(self, difficulty=Difficulty.MEDIUM):
        if difficulty != self.difficulty:
            self.difficulty = difficulty
            self.clear()

            for x in range(0, get_colors_for_difficulty(difficulty)):
                ball = BallBox.new_from_id(x, False, True)
                ball.set_draggable(True)
                self.attach(ball, x + 1, 0, 1, 1)

                idx = ball.connect("id-changed", self._id_changed_cb)
                self.callback_ids[idx] = ball

                self.balls.append(ball)

            self.show_all()

        else:
            for ball in self.balls:
                ball.set_draggable(True)

    def _id_changed_cb(self, ball):
        self.emit("data-changed")
