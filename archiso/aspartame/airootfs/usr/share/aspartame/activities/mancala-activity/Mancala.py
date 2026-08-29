#!/usr/bin/python3
# Mancala.py
"""
    Copyright (C) 2011  Peter Hewitt

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

"""
import g,pygame,utils,sys,buttons,load_save
import manc
try:

    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk
except:
    pass

class Mancala:

    def __init__(self):
        self.journal=True # set to False if we come in via main()
        self.canvas=None # set to the pygame canvas if we come in via activity.py

    def display(self):
        g.screen.fill((0,255,255))
        utils.display_number(g.player,g.player_c,g.font3,utils.ORANGE)
        utils.display_number1(g.wizard,g.wizard_lc,g.font3,utils.ORANGE)
        img=g.xo_grey
        if g.state in (1,2,3): img=g.xo
        g.screen.blit(img,g.xo_xy)
        img=g.magician_grey
        if g.state in (4,5,6): img=g.magician
        g.screen.blit(img,g.magician_xy)
        buttons.draw()
        self.manc.draw()

    def do_click(self):
        if g.state==1: self.manc.click()
    
    def update(self):
        self.manc.do_anims()
        if g.state in (2,3):
            self.manc.player_update()
        elif g.state==4:
            pygame.time.delay(1000)
            dish=self.manc.wizard_move()
            if dish==0: g.state=1
            else: self.manc.wizard_click(dish)
        elif g.state in (5,6):
            self.manc.wizard_update()
        if g.state==1 and not self.manc.player_ok(): g.state=4
        elif g.state==4 and not self.manc.wizard_ok(): g.state=1
        
    def do_button(self,bu):
        if bu=='new': self.manc.setup()

    def do_key(self,key):
        if key in g.SQUARE: self.do_button('new'); return
        if key==pygame.K_v: g.version_display=not g.version_display; return
        if g.state==1:
            if key in g.NUMBERS:
                n=g.NUMBERS[key]
                self.manc.do_click(n); self.manc.set_mouse();return
            if key in g.CROSS:
                self.manc.do_click(self.manc.dish_n); return
            if key in g.RIGHT:
                self.manc.dish_n+=1
                if self.manc.dish_n==7: self.manc.dish_n=1
                self.manc.set_mouse()
                return
            if key in g.LEFT:
                self.manc.dish_n-=1
                if self.manc.dish_n==0: self.manc.dish_n=6
                self.manc.set_mouse()
                return

    def buttons_setup(self):
        buttons.Button('new',(g.sx(30),g.sy(2)))

    def flush_queue(self):
        flushing=True
        while flushing:
            flushing=False
            if self.journal:
                while Gtk.events_pending(): Gtk.main_iteration()
            for event in pygame.event.get(): flushing=True

    def run(self):
        # g.init and self.manc require that we know the display size first
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                return
            elif event.type == pygame.VIDEORESIZE:
                pygame.display.set_mode(event.size, pygame.RESIZABLE)
                break
        g.init()
        if not self.journal: utils.load()
        self.manc=manc.Manc()
        self.manc.setup()
        load_save.retrieve()
        self.buttons_setup()
        if self.canvas!=None: self.canvas.grab_focus()
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
                    self.manc.check_mouse()
                    g.redraw=True
                    if self.canvas!=None: self.canvas.grab_focus()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    g.redraw=True
                    if event.button==1:
                        bu=buttons.check()
                        if bu!='': self.do_button(bu)
                        else: self.do_click()
                        self.flush_queue()
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
            self.update()
            if g.redraw:
                self.display()
                if g.version_display: utils.version_display()
                g.screen.blit(g.pointer,g.pos)
                pygame.display.flip()
                g.redraw=False
            g.clock.tick(40)

if __name__=="__main__":
    pygame.init()
    pygame.display.set_mode((1024,768),pygame.FULLSCREEN)
    game=Mancala()
    game.journal=False
    game.run()
    pygame.display.quit()
    pygame.quit()
    sys.exit(0)
