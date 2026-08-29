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

from utils import get_ball_image
from utils import get_random_ball
from utils import make_ball_pixbuf
from utils import get_eraser_image
from utils import get_result_ball_image

from constants import BallType
from constants import BALL_SIZE
from constants import DRAG_ACTION
from constants import DRAG_TARGETS
from constants import IGNORE_TARGETS
from constants import ResultBallType

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject


class BallBox(Gtk.EventBox):

    __gsignals__ = {
        "id-changed": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [])
    }

    def __init__(self, change_background=True, origin=False):
        Gtk.EventBox.__init__(self)

        self.origin = origin
        self.eraser = False
        self.draggable = False
        self.drag_dest = False
        self.ball = BallType.NULL
        self.image = None

        self.__drag_dest_id = None

        if change_background:
            self.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(1000, 1000, 1000))

        self.make_image()
        self.connect("drag-data-get", self.__get_drag_data)

    @classmethod
    def new_from_id(self, ballid, change_background=True, origin=False):
        ball = BallBox(change_background, origin)
        ball.set_ball(ballid)

        return ball

    def __get_drag_data(self, widget, drag_context, data, info, time):
        data.set_text(str(self.ball), -1)

    def __drag_drop_cb(self, widget, drag_context, x, y, time):
        ball = Gtk.drag_get_source_widget(drag_context)
        if not self.eraser:
            self.set_ball(ball.ball)
            self.set_draggable(self.ball != BallType.NULL)
            self.set_dest_drag(self.ball == BallType.NULL)

        if not ball.origin:
            ball.set_ball(BallType.NULL)
            ball.set_draggable(False)
            ball.set_dest_drag(True)

        if self.eraser and not ball.origin:
            ball.emit("id-changed")

        elif not self.eraser:
            self.emit("id-changed")

    def set_ball(self, ballid):
        self.ball = ballid
        self.make_image()

    def set_draggable(self, draggable):
        if draggable == self.draggable:
            return

        self.draggable = draggable
        if self.draggable:
            self.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, DRAG_TARGETS, DRAG_ACTION)

            if self.ball is not None:
                self.drag_source_set_icon_pixbuf(make_ball_pixbuf(self.ball))
            else:
                self.drag_source_set_icon_pixbuf(make_ball_pixbuf(BallType.NULL))

        else:
            self.drag_source_set(Gdk.ModifierType.BUTTON5_MASK, IGNORE_TARGETS, DRAG_ACTION)

    def set_dest_drag(self, dest):
        if dest == self.drag_dest:
            return

        self.drag_dest = dest

        if self.__drag_dest_id is not None:
            self.disconnect(self.__drag_dest_id)

        if self.drag_dest:
            self.drag_dest_set(Gtk.DestDefaults.ALL, DRAG_TARGETS, DRAG_ACTION)

        else:
            self.drag_dest_set(Gtk.DestDefaults.ALL, IGNORE_TARGETS, DRAG_ACTION)

        self.__drag_dest_id = self.connect("drag-drop", self.__drag_drop_cb)

    def make_image(self):
        if self.image is not None:
            self.remove(self.image)
            del self.image

        if self.ball == BallType.NULL:
            self.image = Gtk.Image()
            self.image.set_size_request(BALL_SIZE, BALL_SIZE)

        else:
            self.image = get_ball_image(self.ball)

        self.add(self.image)
        self.image.show()


class ResultBallBox(BallBox):

    def __init__(self):
        BallBox.__init__(self, False)

    @classmethod
    def new_from_id(self, ballid):
        ball = ResultBallBox()
        ball.set_ball(ballid)

        return ball

    def make_image(self):
        if self.image is not None:
            self.remove(self.image)
            del self.image

        if self.ball == ResultBallType.NULL:
            self.image = Gtk.Image()
            self.image.set_size_request(16, 16)

        else:
            self.image = get_result_ball_image(self.ball)

        self.add(self.image)
        self.image.show()


class EraserBallBox(BallBox):

    def __init__(self):
        BallBox.__init__(self, True, True)

        self.eraser = True
        self.set_dest_drag(True)

    def make_image(self):
        if self.image is not None:
            self.remove(self.image)
            del self.image

        self.image = get_eraser_image()
        self.add(self.image)
        self.image.show()
