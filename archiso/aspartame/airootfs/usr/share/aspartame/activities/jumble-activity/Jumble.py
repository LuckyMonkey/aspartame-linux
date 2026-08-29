#!/usr/bin/python
# Jumble.py


# Copyright (C) 2010  Peter Hewitt
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


import g
import pygame
import utils
import sys
import buttons
import jum
import load_save
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class Jumble:

    def __init__(self):
        # set to False if we come in via main()
        self.journal = True
        # set to the pygame canvas if we come in via activity.py
        self.canvas = None
        self.duration = 800
        self.setup_objects = False

    def display(self):
        g.screen.fill((128, 0, 0))
        buttons.draw()
        self.objects.draw()

    def do_button(self, bu):
        if bu == 'new':
            self.setup_ms = pygame.time.get_ticks()
            g.setup_on = True
        if bu == 'next':
            self.objects.next1()

    def do_key(self, key):
        if key in g.SQUARE:
            if buttons.active('new'):
                self.do_button('new')
                return
        if key in g.CIRCLE:
            if buttons.active('next'):
                self.do_button('next')
                return
        if key == pygame.K_v:
            g.version_display = not g.version_display
            return

    def buttons_setup(self):
        cx = g.sx(30.5)
        buttons.Button('new', (cx, g.sy(3)))
        buttons.Button('next', (cx, g.sy(5.5)))

    def flush_queue(self):
        flushing = True
        while flushing:
            flushing = False
            if self.journal:
                while Gtk.events_pending():
                    Gtk.main_iteration()
            for event in pygame.event.get():
                flushing = True

    def run(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.VIDEORESIZE:
                pygame.display.set_mode(event.size, pygame.RESIZABLE)
                break
        g.init()
        if not self.journal:
            utils.load()
        load_save.retrieve()
        self.buttons_setup()
        self.objects = jum.Objects()
        self.setup_ms = pygame.time.get_ticks() - self.duration
        self.objects.setup()
        g.setup_on = True
        if self.canvas is not None:
            self.canvas.grab_focus()
        ctrl = False
        pygame.key.set_repeat(600, 120)
        key_ms = pygame.time.get_ticks()
        self.running = True
        while self.running:
            if self.journal:
                # Pump GTK messages.
                while Gtk.events_pending():
                    Gtk.main_iteration()

            # Pump PyGame messages.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if not self.journal:
                        utils.save()
                    self.running = False
                elif event.type == pygame.MOUSEMOTION:
                    g.pos = event.pos
                    g.redraw = True
                    self.objects.update()
                    if self.canvas is not None:
                        self.canvas.grab_focus()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    g.redraw = True
                    if event.button == 1:
                        if self.objects.click():
                            if self.objects.complete:
                                buttons.off('next')
                        else:
                            self.display()
                            bu = buttons.check()
                            if bu != '':
                                self.do_button(bu)
                    if event.button == 3:
                        if buttons.active('next'):
                            self.do_button('next')
                    self.flush_queue()
                elif event.type == pygame.KEYDOWN:
                    # throttle keyboard repeat
                    if pygame.time.get_ticks() - key_ms > 110:
                        key_ms = pygame.time.get_ticks()
                        if ctrl:
                            if event.key == pygame.K_q:
                                if not self.journal:
                                    utils.save()
                                self.running = False
                                break
                            else:
                                ctrl = False
                        if event.key in (pygame.K_LCTRL, pygame.K_RCTRL):
                            ctrl = True
                            break
                        self.do_key(event.key)
                        g.redraw = True
                        self.flush_queue()
                elif event.type == pygame.KEYUP:
                    ctrl = False
            if not self.running:
                break
            if g.setup_on:
                g.redraw = True
                _time = pygame.time.get_ticks() - self.setup_ms
                self.objects.play_anim(abs(1 - _time/self.duration))
                if _time > self.duration and not self.setup_objects:
                    self.objects.setup()
                    self.setup_objects = True
                if _time > 2 * self.duration:
                    self.objects.play_anim(1)
                    g.setup_on = False
                    self.setup_objects = False
                    buttons.on('next')
            if g.redraw:
                self.display()
                if g.version_display:
                    utils.version_display()
                g.screen.blit(g.pointer, g.pos)
                pygame.display.flip()
                g.redraw = False
            g.clock.tick(40)


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_mode((1024, 768), pygame.FULLSCREEN)
    game = Jumble()
    game.journal = False
    game.run()
    pygame.display.quit()
    pygame.quit()
    sys.exit(0)
