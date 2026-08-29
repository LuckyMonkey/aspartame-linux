# g.py - globals
import pygame,utils,random

app='Mancala'; ver='1.0'
ver='4.0'
# speed changed
# O key added
ver='4.1'
# dish numbers added
# tablet mode
ver='4.2'
# tick button for click as well as up & down
ver='4.3'
# standard gamepad keys
ver='4.4'
# no up & down arrows, right arrow re-instated
ver='4.5'
# arrow keys move mouse
ver='4.6'
# mouse hide removed
# mouse repositioned
ver='4.7'
# MOUSEMOTION fake cursor
ver='4.8'
# pygame.mouse.set_visible(False) moved to g.py
ver='4.9'
# buttons.py - redraw pointer when button down
ver='21'
ver='22'
# flush_queue() doesn't use gtk on non-XO

UP=(264,273)
DOWN=(258,274)
LEFT=(260,276)
RIGHT=(262,275)
CROSS=(259,120)
CIRCLE=(265,111)
SQUARE=(263,32)
TICK=(257,13)
NUMBERS={pygame.K_1:1,pygame.K_2:2,pygame.K_3:3,pygame.K_4:4,\
           pygame.K_5:5,pygame.K_6:6}

def init(): # called by run()
    random.seed()
    global redraw
    global screen,w,h,font1,font2,font3,clock
    global factor,offset,imgf,message,version_display
    global pos,pointer
    redraw=True
    version_display=False
    screen = pygame.display.get_surface()
    pygame.display.set_caption(app)
    screen.fill((70,0,70))
    pygame.display.flip()
    w,h=screen.get_size()
    if float(w)/float(h)>1.5: #widescreen
        offset=(w-4*h/3)/2 # we assume 4:3 - centre on widescreen
    else:
        h=int(.75*w) # allow for toolbar - works to 4:3
        offset=0
    factor=float(h)/24 # measurement scaling factor (32x24 = design units)
    imgf=float(h)/900 # image scaling factor - all images built for 1200x900
    clock=pygame.time.Clock()
    if pygame.font:
        t=int(50*imgf); font1=pygame.font.Font(None,t)
        t=int(70*imgf); font2=pygame.font.Font(None,t)
        t=int(100*imgf); font3=pygame.font.Font(None,t)
    message=''
    pos=pygame.mouse.get_pos()
    pointer=utils.load_image('pointer.png',True)
    pygame.mouse.set_visible(False)
    
    # this activity only
    global player,wizard,player_c,wizard_lc
    global xo,magician,xo_xy,magician_xy,xo_grey,magician_grey,blue,ring
    global state
    player=0; wizard=0; player_c=(sx(30),sy(20)); wizard_lc=(sx(5.1),sy(1.5))
    xo=utils.load_image("xo.png",True); xo_xy=(sx(29),sy(15.9))
    xo_grey=utils.load_image("xo_grey.png",True)
    magician=utils.load_image("magician.png",True); magician_xy=(sx(.3),sy(.5))
    magician_grey=utils.load_image("magician_grey.png",True)
    blue=utils.load_image("blue.png",True)
    ring=utils.load_image("ring.png",True)
    state=1
    # 1 waiting for player click
    # 2 player move
    # 3 player green move
    # 4 waiting for wizard move
    # 5 wizard move
    # 6 wizard green move
    # 7 player win
    # 8 wizard win
    # 9 draw
    
def sx(f): # scale x function
    return f*factor+offset+.5

def sy(f): # scale y function
    return f*factor+.5
