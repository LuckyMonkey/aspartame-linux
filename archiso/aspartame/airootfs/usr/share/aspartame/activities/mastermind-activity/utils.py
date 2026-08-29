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
import random

from constants import BallType
from constants import BALL_SIZE
from constants import LOCAL_DIR
from constants import Difficulty
from constants import ResultBallType

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GdkPixbuf


def get_ball_name(ballid):
    if ballid == BallType.NULL:
        return "ball-white"

    elif ballid == BallType.RED:
        return "ball-red"

    elif ballid == BallType.GREEN:
        return "ball-green"

    elif ballid == BallType.SKYBLUE:
        return "ball-skyblue"

    elif ballid == BallType.BROWN:
        return "ball-brown"

    elif ballid == BallType.PURPLE:
        return "ball-purple"

    elif ballid == BallType.PINK:
        return "ball-pink"

    elif ballid == BallType.BLUE:
        return "ball-blue"

    elif ballid == BallType.YELLOW:
        return "ball-yellow"


def get_result_ball_name(ballid):
    if ballid == ResultBallType.NULL:
        return "ball-white"

    elif ballid == ResultBallType.WHITE:
        return "ball-correct1"

    elif ballid == ResultBallType.BLACK:
        return "ball-correct2"


def get_ball_image_path(ballid):
    name = get_ball_name(ballid)
    return os.path.join(LOCAL_DIR, "icons", name + ".svg")


def get_result_ball_image_path(ballid):
    name = get_result_ball_name(ballid)
    return os.path.join(LOCAL_DIR, "icons", name + ".svg")


def make_ball_pixbuf(ballid):
    path = get_ball_image_path(ballid)
    return GdkPixbuf.Pixbuf.new_from_file_at_size(path, BALL_SIZE, BALL_SIZE)


def get_ball_image(ballid):
    pixbuf = make_ball_pixbuf(ballid)
    return Gtk.Image.new_from_pixbuf(pixbuf)


def get_result_ball_image(ballid):
    return Gtk.Image.new_from_file(get_result_ball_image_path(ballid))


def get_random_ball(difficulty):
    colors = [
        BallType.RED,
        BallType.GREEN,
        BallType.SKYBLUE,
        BallType.BROWN,
        BallType.PURPLE,
        BallType.PINK,
        BallType.BLUE,
        BallType.YELLOW
    ]

    colors = colors[:get_colors_for_difficulty(difficulty)]
    return random.choice(colors)


def get_eraser_image():
    path = os.path.join(LOCAL_DIR, "icons/eraser.svg")
    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(path, BALL_SIZE, BALL_SIZE)
    return Gtk.Image.new_from_pixbuf(pixbuf)


def get_columns_for_difficulty(difficulty):
    if difficulty == Difficulty.EASY:
        return 2

    elif difficulty == Difficulty.MEDIUM:
        return 3

    elif difficulty == Difficulty.ADVANCED:
        return 4

    elif difficulty == Difficulty.EXPERT:
        return 5


def get_colors_for_difficulty(difficulty):
    if difficulty == Difficulty.EASY:
        return 4

    elif difficulty == Difficulty.MEDIUM:
        return 6

    elif difficulty == Difficulty.ADVANCED:
        return 8

    elif difficulty == Difficulty.EXPERT:
        return 8
