# g.py - globals
import pygame,utils,random

app='Across and Down'; ver='1'
ver='21'
ver='22'
# g.percent reset on new game/replay
ver='23'
# added 100% count
ver='24'
# only one 100% per game

UP=(pygame.K_KP8, pygame.K_UP)
DOWN=(pygame.K_KP2, pygame.K_DOWN)
LEFT=(pygame.K_KP4, pygame.K_LEFT)
RIGHT=(pygame.K_KP6, pygame.K_RIGHT)
CROSS=(pygame.K_KP3, pygame.K_x)
CIRCLE=(pygame.K_KP9, pygame.K_o)
SQUARE=(pygame.K_KP7, pygame.K_SPACE)
TICK=(pygame.K_KP1, pygame.K_RETURN)
NUMBERS={pygame.K_1:1,pygame.K_2:2,pygame.K_3:3,pygame.K_4:4,\
           pygame.K_5:5,pygame.K_6:6,pygame.K_7:7,pygame.K_8:8,\
           pygame.K_9:9,pygame.K_0:0}

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
    screen.fill((255,255,192))
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
        t=int(60*imgf); font1=pygame.font.Font(None,t)
        t=int(80*imgf); font2=pygame.font.Font(None,t)
        t=int(40*imgf); font3=pygame.font.Font(None,t)
    message=''
    pos=pygame.mouse.get_pos()
    pointer=utils.load_image('pointer.png',True)
    pygame.mouse.set_visible(False)
    
    # this activity only
    global level,best,bgd,x0,message_c,scores,scores_c
    global score,target,score_c,target_c,vinc,percent,percent_xy,best_xy
    global glow,ms
    global help_img,help_on,help_cxy
    global count,count_c,complete
    best=0
    bgd=utils.load_image('bgd.png',False); x0=sx(0)
    message_c=(sx(16),sy(2))
    scores=utils.load_image('scores.png',False)
    scores_c=(sx(5.7),sy(11))
    score=0; target=0
    y=1.18-.3
    score_c=(sx(1.8),sy(y)); target_c=(sx(1.8),sy(y+1.32))
    vinc=pygame.Rect(sx(1.17),sy(y+.52),sy(1.3),sy(.16))
    percent=None; percent_xy=(sx(2.9),sy(y+.08))
    best_xy=(sx(25.5),sy(y-.5))
    glow=utils.load_image('glow.png',True); ms=None
    help_img=utils.load_image('help.png',False); help_cxy=(sx(16),sy(10.1))
    help_on=False
    count=0; count_c=(sx(28.5),best_xy[1]+sy(1.4)); complete=False
   
def sx(f): # scale x function
    return int(f*factor+offset+.5)

def sy(f): # scale y function
    return int(f*factor+.5)
