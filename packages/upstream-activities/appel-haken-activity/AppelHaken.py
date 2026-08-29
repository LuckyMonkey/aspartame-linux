#!/usr/bin/env python3
# AppelHaken.py
"""
    Copyright (C) 2010  Peter Hewitt

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

"""
import g, pygame, utils, sys, buttons, ah, slider, load_save
try:
    from gi.repository import Gtk
except:
    pass


class AppelHaken:

    def __init__(self):
        self.journal=True # set to False if we come in via main()
        self.canvas=None # set to the pygame canvas if we come in via activity.py

    def display(self):
        g.screen.fill((0,0,70))
        buttons.draw()
        self.grid.draw()
        self.slider.draw()
        utils.display_number(g.score,self.score_cxy,g.font2,utils.CREAM)
        if self.grid.complete():
            utils.centre_blit(g.screen,g.smiley,self.smiley_cxy)

    def do_button(self, bu):
        if bu=='reset': self.grid.reset(); buttons.clear()
        elif bu=='new': self.grid.setup(); buttons.clear()
        else:
            if not self.grid.complete():
                self.grid.colour_ind=int(bu)

    def do_key(self, key):
        if key in g.SQUARE: self.do_button('new'); return
        if key in g.CIRCLE: self.do_button('reset'); return
        if key in g.TICK:
            self.change_level(); return
        if key==pygame.K_v: g.version_display=not g.version_display; return
        if not self.grid.complete():
            if key in g.NUMBERS:
                buttons.clear()
                self.grid.colour_ind=g.NUMBERS[key]
                buttons.stay_down(str(self.grid.colour_ind))

    def change_level(self):
        g.level+=1
        if g.level>self.slider.steps: g.level=1
        self.grid.new1(); self.grid.setup(); buttons.clear()

    def buttons_setup(self):
        cx=g.sx(30.5)
        cy=g.sy(1.6); dy=g.sy(3)
        for i in range(1,5):
            buttons.Button(str(i),(cx,cy))
            cy+=dy
        buttons.Button('reset',(cx,g.sy(17.5)))
        buttons.Button('new',(cx,g.sy(20.5)))
        self.score_cxy=(cx,g.sy(14)); self.smiley_cxy=(g.sx(3),g.sy(20.5))

    def flush_queue(self):
        flushing=True
        while flushing:
            flushing=False
            if self.journal:
                while Gtk.events_pending(): Gtk.main_iteration()
            for event in pygame.event.get(): flushing=True

    def run(self):
        g.init()
        if not self.journal: utils.load()
        load_save.retrieve()
        self.buttons_setup()
        self.slider=slider.Slider(g.sx(16),g.sy(20.5),9,utils.GREEN)
        self.grid=ah.Grid()
        self.grid.new1(); self.grid.setup()
        if self.canvas!=None: 
            self.canvas.grab_focus()
        ctrl=False
        pygame.key.set_repeat(600,120); key_ms=pygame.time.get_ticks()
        going=True
        while going:
            if self.journal:
                # Pump GTK messages.
                while Gtk.events_pending(): Gtk.main_iteration()

            # Pump PyGame messages.
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    if not self.journal: utils.save()
                    going=False
                elif event.type == pygame.MOUSEMOTION:
                    g.pos=event.pos
                    g.redraw=True
                    if self.canvas!=None: self.canvas.grab_focus()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    g.redraw=True
                    if event.button==1:
                        if self.grid.click():
                            pass
                        elif self.slider.mouse():
                            self.grid.new1(); self.grid.setup(); buttons.clear() # level changed
                        else:
                            bu=buttons.check()
                            if bu!='': self.do_button(bu)
                            else: self.grid.colour_ind=0
                        self.flush_queue()
                    elif event.button==3:
                        self.do_button('reset')
                elif event.type == pygame.KEYDOWN:
                    # throttle keyboard repeat
                    if pygame.time.get_ticks()-key_ms>110:
                        key_ms=pygame.time.get_ticks()
                        if ctrl:
                            if event.key==pygame.K_q:
                                if not self.journal: utils.save()
                                going=False; break
                            else:
                                ctrl=False
                        if event.key in (pygame.K_LCTRL,pygame.K_RCTRL):
                            ctrl=True; break
                        self.do_key(event.key); g.redraw=True
                        self.flush_queue()
                elif event.type == pygame.KEYUP:
                    ctrl=False
            if not going: break
            if self.grid.complete():
                buttons.clear()
            if g.redraw:
                self.display()
                if g.version_display: utils.version_display()
                g.screen.blit(g.pointer,g.pos)
                pygame.display.flip()
                g.redraw=False
            self.score=g.score; self.level=g.level
            g.clock.tick(40)

if __name__=="__main__":
    pygame.init()
    pygame.display.set_mode((1024,768),pygame.FULLSCREEN)
    game=AppelHaken()
    game.journal=False
    game.run()
    pygame.display.quit()
    pygame.quit()
    sys.exit(0)
