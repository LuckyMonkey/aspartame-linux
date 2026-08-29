# g.py - globals
import pygame,utils,random

app='Appel Haken'; ver='1.0'
ver='2.0'
# proper cursor
ver='2.1'
# number keys properly implemented
ver='2.2'
# click on bgd -> no colour
# reset clears clashes
ver='4.0'
# 5 & o keys
ver='21'
ver='22'
# flush_queue() doesn't use gtk on non-XO
ver='23'
# right click=reset
ver='24'
# ignore arrow keys
# only score each layout once

UP=(264,273)
DOWN=(258,274)
LEFT=(260,276)
RIGHT=(262,275)
CROSS=(259,120)
CIRCLE=(265,111)
SQUARE=(263,32)
TICK=(257,13)
NUMBERS={pygame.K_1:1,pygame.K_2:2,pygame.K_3:3,pygame.K_4:4}

def init(): # called by run()
    random.seed()
    global redraw
    global screen,w,h,font1,font2,clock
    global factor,offset,imgf,message,version_display
    global pos,pointer
    redraw=True
    version_display=False; frame_rate=0
    screen = pygame.display.get_surface()
    screen.fill((80,0,80)); pygame.display.flip()
    w,h=screen.get_size()
    if float(w)/float(h)>1.5: #widescreen
        offset=(w-4*h/3)/2 # we assume 4:3 - centre on widescreen
    else:
        h=int(.75*w) # allow for toolbar - works to 4:3
        offset=0
    pygame.display.set_caption(app)
    clock=pygame.time.Clock()
    factor=float(h)/24 # measurement scaling factor (32x24 = design units)
    imgf=float(h)/900 # image scaling factor - all images built for 1200x900
    if pygame.font:
        t=int(40*imgf); font1=pygame.font.Font(None,t)
        t=int(80*imgf); font2=pygame.font.Font(None,t)
    message=''
    pos=pygame.mouse.get_pos()
    pointer=utils.load_image('pointer.png',True)
    pygame.mouse.set_visible(False)
    
    # this activity only
    global score,level,smiley,scored
    score=0; level=1
    smiley=utils.load_image('smiley.png',True)
    scored=False
    
def sx(f): # scale x function
    return f*factor+offset

def sy(f): # scale y function
    return f*factor
