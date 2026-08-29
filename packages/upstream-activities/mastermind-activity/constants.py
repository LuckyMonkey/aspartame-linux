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

import os

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import Gdk


LOCAL_DIR = os.path.dirname(os.path.realpath(__file__))

DRAG_TARGETS = [Gtk.TargetEntry.new("BALL", Gtk.TargetFlags.SAME_APP, 0)]
IGNORE_TARGETS = []
DRAG_ACTION = Gdk.DragAction.MOVE

BALL_SIZE = (Gdk.Screen.height() - 200) / 10


class BallType:
    NULL    = -1
    RED     = 0
    GREEN   = 1
    SKYBLUE = 2
    BROWN   = 3
    PURPLE  = 4
    PINK    = 5
    BLUE    = 6
    YELLOW  = 7


class ResultBallType:
    NULL  = -1
    WHITE = 1
    BLACK = 2


class Difficulty:
    EASY     = 0
    MEDIUM   = 1
    ADVANCED = 2
    EXPERT   = 3
