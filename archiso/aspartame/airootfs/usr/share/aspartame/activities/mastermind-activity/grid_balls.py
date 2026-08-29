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
from constants import BallType
from constants import Difficulty
from result_box import ResultBox
from utils import get_columns_for_difficulty

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject


class GridBalls(Gtk.Grid):

    __gsignals__ = {
        "data-changed": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, []),
    }

    def __init__(self):
        Gtk.Grid.__init__(self)

        self.balls = {}
        self.result_boxes = []
        self.callbacks_ids = {}
        self.level = None
        self.difficulty = Difficulty.MEDIUM

        self.set_row_spacing(2)
        self.set_column_spacing(2)

        self.show_all()

    def clear(self):
        for x in list(self.balls.keys()):
            for ball in self.balls[x]:
                if ball is not None:
                    self.remove(ball)

                del ball

        for box in self.result_boxes:
            self.remove(box)
            del box

        del self.balls
        del self.result_boxes

        self.balls = {}
        self.result_boxes = []
        self.level = 0

        self.clear_callbacks()

        for x in range(0, get_columns_for_difficulty(self.difficulty)):
            self.balls[x] = [None] * 10

    def reset(self, difficulty=None):
        if difficulty is not None:
            self.difficulty = difficulty

        self.clear()

        x = -1
        y = 0

        columns = get_columns_for_difficulty(self.difficulty)

        for i in range(0, columns * 10):
            x += 1

            if x >= columns:
                x = 0
                y += 1

            box = BallBox()
            self.attach(box, x, y, 1, 1)

            self.balls[x][9 - y] = box

        for i in range(0, 10):
            box = ResultBox(columns)
            self.attach(box, columns, 9 - i, 1, 1)
            self.result_boxes.append(box)

        self.set_drag_level()
        self.show_all()

    def set_ball(self, x, y, ballid):
        self.balls[x][y].set_ball(ballid)

    def set_drag_level(self):
        self.clear_callbacks()

        for x in range(0, get_columns_for_difficulty(self.difficulty)):
            for y in range(0, 10):
                ball = self.balls[x][y]
                ball.set_dest_drag(y == self.level)
                ball.set_draggable(y == self.level and ball.ball != BallType.NULL)

                if y == self.level:
                    idx = ball.connect("id-changed", self._id_changed_cb)
                    self.callbacks_ids[idx] = ball

    def get_level_data(self):
        level = []
        if self.level < 10:
            for x in range(0, get_columns_for_difficulty(self.difficulty)):
                ball = self.balls[x][self.level]
                level.append(ball.ball)

        return level

    def next_level(self):
        self.level += 1
        self.set_drag_level()
        self.emit("data-changed")

    def set_data(self, level, user):
        self.result_boxes[self.level].set_data(level, user)
        self.next_level()

    def get_all_data(self):
        data = {
            "level": self.level,
            "balls": {}
        }

        for x in range(0, get_columns_for_difficulty(self.difficulty)):
            data["balls"][x] = []
            for y in range(0, 10):
                data["balls"][x].append(self.balls[x][y].ball)

        return data

    def set_all_data(self, data):
        self.difficulty = data["difficulty"]
        self.clear()

        self.level = data["level"]
        columns = get_columns_for_difficulty(self.difficulty)

        for x in range(0, columns):
            for y in range(0, 10):
                ballid = data["balls"][x][y]
                ball = BallBox()
                ball.set_ball(ballid)
                self.attach(ball, x, 9 - y, 1, 1)
                self.balls[x][y] = ball

        self.set_drag_level()

        for i in range(0, 10):
            box = ResultBox()
            self.attach(box, columns, 9 - i, 1, 1)
            self.result_boxes.append(box)

            if i < self.level:
                user = []
                for x in range(0, columns):
                    user.append(data["balls"][x][i])

                box.set_data(data["correct"], user)

        self.show_all()

    def clear_callbacks(self, unset=False):
        for idx in list(self.callbacks_ids.keys()):
            ball = self.callbacks_ids[idx]
            ball.disconnect(idx)

            if unset:
                ball.set_draggable(False)
                ball.set_dest_drag(False)

        del self.callbacks_ids
        self.callbacks_ids = {}

    def game_over(self):
        self.clear_callbacks(True)

    def _id_changed_cb(self, ball):
        self.emit("data-changed")
