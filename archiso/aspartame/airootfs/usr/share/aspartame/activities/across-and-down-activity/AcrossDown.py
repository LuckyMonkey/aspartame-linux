#!/usr/bin/python
# AcrossDown.py
"""
    Copyright (C) 2011  Peter Hewitt

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

"""
import g,pygame,utils,sys,load_save,buttons,acr,letter_keys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class AcrossDown:

    def __init__(self, activity):
        self.journal = True  # set to False if we come in via main()
        self.canvas = None

    def display(self):
        g.screen.fill((255,255,192))
        g.screen.blit(g.bgd,(g.x0,0))
        self.acr.draw()
        utils.centre_blit(g.screen,g.scores,g.scores_c)
        utils.display_number(g.score,g.score_c,g.font1)
        pygame.draw.rect(g.screen,utils.BLACK,g.vinc)
        utils.display_number(g.target,g.target_c,g.font1)
        utils.text_blit1(g.screen,g.percent,g.font1,g.percent_xy,\
                         utils.BLACK,False)
        if g.best>0:
            s='Best: '+str(g.best)+'%'
            utils.text_blit1(g.screen,s,g.font1,g.best_xy,utils.BLACK,False)
        if g.count==2:
            utils.text_blit(g.screen,'twice',g.font3,g.count_c,utils.ORANGE,False)
        if g.count>2:
            s=str(g.count)+' times'
            utils.text_blit(g.screen,s,g.font3,g.count_c,utils.ORANGE,False)
        buttons.draw()
        if self.acr.message!=None:
            utils.message1(g.screen,g.font1,self.acr.message,g.message_c)
        if g.help_on:
            utils.centre_blit(g.screen,g.help_img,g.help_cxy)

    def do_click(self):
        l=self.acr.which_oval()
        if l!=None: self.acr.do_letter(l); return True
        cell=self.acr.which_cell()
        if cell!=None: self.acr.green=cell.ind; return True
        return False

    def do_button(self,bu):
        if bu=='new': self.acr.setup(); return
        if bu=='replay': self.acr.replay(); return
        if bu=='clear': self.acr.clear(); return
        if bu=='try': self.acr.check(); return
        if bu=='help': g.help_on=not g.help_on

    def do_key(self,key):
        if key==pygame.K_1: g.version_display=not g.version_display; return
        l=None
        if key in (pygame.K_BACKSPACE,pygame.K_DELETE,pygame.K_SPACE): l=' '
        else: l=letter_keys.which(key)
        if l!=None: self.acr.do_letter(l); return
        if key in g.SQUARE: self.do_button('new'); return
        if key in g.LEFT: self.acr.left(); return
        if key in g.RIGHT: self.acr.right(); return
        if key in g.UP: self.acr.up(); return
        if key in g.DOWN: self.acr.down(); return
        if key in g.TICK: self.acr.check(); return
        if key in g.CROSS: self.do_click(); return
        if key in g.CIRCLE: g.help_on=not g.help_on; return

    def buttons_setup(self):
        cy=g.sy(19.8)
        buttons.Button('new',(g.sx(30),cy),caption='new game')
        buttons.Button('replay',(g.sx(2),cy),caption='replay')
        cx=g.sx(26)
        buttons.Button('try',(cx,g.sy(8.5)),caption='try')
        buttons.Button('clear',(cx,g.sy(13)),caption='clear')
        buttons.Button('help',(g.sx(30),g.sy(3.3)),caption='help')

    def flush_queue(self):
        flushing=True
        while flushing:
            flushing=False
            if self.journal:
                while Gtk.events_pending(): Gtk.main_iteration()
            for event in pygame.event.get(): flushing=True

    def run(self):
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                return
            elif event.type == pygame.VIDEORESIZE:
                pygame.display.set_mode(event.size, pygame.RESIZABLE)
                break
        g.init()
        if not self.journal: utils.load()
        self.acr=acr.Acr()
        load_save.retrieve()
        self.buttons_setup()
        if self.canvas!=None: self.canvas.grab_focus()
        ctrl=False
        pygame.key.set_repeat(600,120); key_ms=pygame.time.get_ticks()
        going=True
        while going:
            if self.journal:
                # Pump Gtk messages.
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
                    self.acr.message=None
                    g.redraw=True
                    if event.button==1:
                        if g.help_on:
                            g.help_on=False
                        elif self.do_click():
                            pass
                        else:
                            bu=buttons.check()
                            if bu!='': self.do_button(bu); self.flush_queue()
                    if event.button==3: g.help_on=not g.help_on
                elif event.type == pygame.KEYDOWN:
                    if event.key not in g.CIRCLE: g.help_on=False
                    self.acr.message=None
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
            self.acr.update()
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
    game=AcrossDown()
    game.journal=False
    game.run()
    pygame.display.quit()
    pygame.quit()
    sys.exit(0)
