# manc.py

import g,utils,random,pygame

# groups & dishes - group is what is moving
#15  14   13   12   11   10  9   8
#    13   12   11   10   9   8
# 0                              7
#     1    2    3    4   5   6
# 0   1    2    3    4   5   6   7

class Dish:
    def __init__(self,cxy):
        self.cxy=cxy; self.n=0; self.orange=False; self.green=False
        
class Group:
    def __init__(self,cxy):
        self.cxy=cxy
        
class Anim:
    def __init__(self): # n,x,y,x2,y2,dx,dy,ms
        self.ms=None
        
class Manc:
    def __init__(self):
        self.cxy=(g.sx(16),g.sy(11))
        self.base=utils.load_image('base.png',True)
        self.top=utils.load_image('top.png',True)
        self.ball=utils.load_image('ball.png',True)
        self.green=utils.load_image('green.png',True)
        self.h4=int(self.green.get_height()/4)
        self.orange=utils.load_image('orange.png',True)
        self.x0=g.sx(3.2); self.y0=self.cxy[1]+g.sy(.2) # wizard dish
        self.dx=g.sy(3.645); self.dy=g.sy(3.7) # between dishes
        # dishes
        self.dishes=[]; x=self.x0; y=self.y0
        for ind in range(8):
            dish=Dish((int(x),int(y))); self.dishes.append(dish)
            if ind==0: y+=self.dy
            if ind==6: y=self.y0; kx=x
            x+=self.dx
        x=kx; y=self.y0-self.dy
        for ind in range(8,14):
            dish=Dish((int(x),int(y))); self.dishes.append(dish)
            x-=self.dx
        # balls
        self.balls=[None,self.ball]
        for ind in range(2,27):
            img=utils.load_image(str(ind)+'.png',True); self.balls.append(img)
        # rectangle 1
        cx,cy=self.dishes[1].cxy
        self.x1=cx-g.sy(1.5); self.x2=self.x1+g.sy(3)
        self.y1=cy-g.sy(3); self.y2=self.y1+g.sy(7)
        # groups
        self.groups=[]; f=2.3
        x=self.x0; y=self.y0+f*self.dy
        for i in range(8):
            group=Group((int(x),int(y))); self.groups.append(group)
            x+=self.dx
        y=self.y0-f*self.dy
        for i in range(8):
            x-=self.dx
            group=Group((int(x),int(y))); self.groups.append(group)
        self.anim=[Anim(),Anim()]
        self.dish_n=1
        self.set_mouse()

    def draw(self):
        utils.centre_blit(g.screen,self.base,self.cxy)
        self.draw_dishes()
        utils.centre_blit(g.screen,self.top,self.cxy)
        self.numbers()
        self.draw_anims()

    def setup(self):
        self.clear()
        ind1=1; ind2=6
        for i in range(2):
            total=0 # number of balls used so far - must be 24 at the end
            nmax=5 # will reduce if we have used too many balls
            for ind in range(ind1,ind2+1):
                if ind==ind2: n=24-total
                else: n=random.randint(3,nmax); total+=n
                if total>18: nmax-=1
                self.dishes[ind].n=n
            ind1=8; ind2=13
        self.dishes[0].n=0; self.dishes[7].n=0
        self.anim[0].ms=None; self.anim[1].ms=None
        g.state=1
        
    def clear(self):
        self.dishes[0].orange=False; self.dishes[7].orange=False
        for ind in range(14): self.dishes[ind].green=False

    def draw_dishes(self):
        for ind in range(14):
            n=self.dishes[ind].n; cx,cy=self.dishes[ind].cxy
            if self.dishes[ind].orange:
                utils.centre_blit(g.screen,self.orange,(cx,cy))
            if self.dishes[ind].green:
                utils.centre_blit(g.screen,self.green,(cx,cy))
            if n>0:
                if n>26: n=26
                utils.centre_blit(g.screen,self.balls[n],(cx,cy))

    def set_mouse(self):
        x,y=self.dishes[self.dish_n].cxy
        y+=self.h4
        pygame.mouse.set_pos((x,y)); g.pos=(x,y)
        
    def check_mouse(self):
        n=self.which()
        if n>0: self.dish_n=n
        
    def numbers(self):
        cy=int(self.y0+g.sy(.1)); dx=g.sy(.05); cyn=int(self.y0+g.sy(.05))
        for i in range(1,7):
            cx=self.dishes[i].cxy[0]-dx
            utils.display_number(str(i),(cx,cy),g.font1,utils.CYAN)
            if i==self.dish_n:
                utils.centre_blit(g.screen,g.ring,(cx,cyn))
        cy=int(self.y0+2*self.dy-g.sy(.1)); k=150; colr=(k,k,k)
        for ind in range(1,7):
            cx=self.dishes[ind].cxy[0]
            utils.display_number(self.dishes[ind].n,(cx,cy),g.font1,colr)
        cy=int(self.y0-2*self.dy-g.sy(.1))
        for ind in range(8,14):
            cx=self.dishes[ind].cxy[0]
            utils.display_number(self.dishes[ind].n,(cx,cy),g.font1,colr)
        ind=0; n=self.dishes[ind].n; cx,cy=self.dishes[ind].cxy
        cxy=(cx,cy-self.dy-g.sy(.8))
        if g.state in (8,9): utils.centre_blit(g.screen,g.blue,cxy)
        utils.display_number(n,cxy,g.font2,utils.CREAM)
        ind=7; n=self.dishes[ind].n; cx,cy=self.dishes[ind].cxy
        cxy=(cx,cy+self.dy+g.sy(.7))
        if g.state in (7,9): utils.centre_blit(g.screen,g.blue,cxy)
        utils.display_number(n,cxy,g.font2,utils.CREAM)

    def which(self):
        x1=self.x1; x2=self.x2
        for i in range(1,7):
            if utils.mouse_in(x1,self.y1,x2,self.y2): return i
            x1+=self.dx; x2+=self.dx
        return 0

    def click(self):
        dish=self.which()
        if dish>0: self.do_click(dish)

    def do_click(self,dish):
        n=self.dishes[dish].n
        if n==0: return
        self.clear()
        self.dishes[dish].n=0
        self.group1=dish
        self.group2=dish+1
        self.n=n
        self.move(n,self.group1,self.group2)
        self.dish_n=dish
        g.state=2
        
    def player_update(self):
        if self.anim[0].ms==None:
            if g.state==3:
                self.dishes[7].n+=self.n
                g.state=4; self.complete()
                return
            if self.group2 not in (0,8,15):
                dish=self.group2
                if self.group2>7: dish-=1
                self.dishes[dish].n+=1 # drop one ball
                self.n-=1
            if self.n==0:
                g.state=4; self.complete()
                if dish==7:
                    self.dishes[7].orange=True
                    g.state=1; self.complete()
                elif self.dishes[dish].n==1 and dish<7:
                    opp=14-dish; n=self.dishes[opp].n
                    if n>0:
                        self.move(1,self.group2,7); self.dishes[dish].n=0
                        self.dishes[opp].n=0
                        self.move(n,(opp+1),8)
                        self.dishes[dish].green=True; self.dishes[opp].green=True
                        self.n=n+1
                        g.state=3
            else:
                self.group1=self.group2; self.group2+=1
                if self.group2==16: self.group2=0
                self.move(self.n,self.group1,self.group2)

    def move(self,n,group1,group2):
        ind=0
        if self.anim[ind].ms!=None: ind=1
        # n,x,y,x2,y2,dx,dy,ms
        a=self.anim[ind]
        a.n=n
        a.x,a.y=self.groups[group1].cxy; a.x2,a.y2=self.groups[group2].cxy
        ng=abs(group1-group2)
        a.dx=(a.x2-a.x)/4.0/ng; a.dy=(a.y2-a.y)/7.0
        a.ms=pygame.time.get_ticks()

    def do_anims(self):
        for ind in range(2):
            a=self.anim[ind]
            if a.ms!=None:
                d=pygame.time.get_ticks()-a.ms
                if d>100:
                    a.x+=a.dx; a.y+=a.dy; a.ms=pygame.time.get_ticks()
                    if abs(a.x-a.x2)<.1 and abs(a.y-a.y2)<.1:
                        a.x=a.x2; a.y=a.y2; a.ms=None
                    g.redraw=True

    def draw_anims(self):
        for ind in range(2):
            a=self.anim[ind]
            if a.ms!=None:
                n=a.n
                if n>0:
                    if n>26: n=26
                    utils.centre_blit(g.screen,self.balls[n],(a.x,a.y))
        
    def wizard_move(self):
        # possible repeat?
        m=1
        for ind in range(13,7,-1):
            if self.dishes[ind].n==m: return ind
            m+=1
        # possible capture?
        for ind in range(13,7,-1):
            n=self.dishes[ind].n
            if n>0:
                final_dish=ind+n
                if final_dish>13: final_dish-=13
                if final_dish>13: final_dish-=13
                if final_dish>7:
                    opp=14-final_dish
                    if self.dishes[opp].n>0:
                        if self.dishes[final_dish].n==0: return ind
                        if final_dish==ind: return ind
        ind=random.randint(8,13)
        for i in range(6):
            if self.dishes[ind].n>0: return ind
            ind+=1
            if ind>13: ind=8
        return 0 # no possible move

    def wizard_click(self,dish):
        self.clear()
        n=self.dishes[dish].n
        self.dishes[dish].n=0
        self.group1=dish+1
        self.group2=dish+2
        self.n=n
        self.move(n,self.group1,self.group2)
        g.state=5; self.complete()

    def wizard_update(self):
        if self.anim[0].ms==None:
            if g.state==6:
                self.dishes[0].n+=self.n
                g.state=1; self.complete()
                return
            if self.group2 not in (0,7,8):
                dish=self.group2
                if self.group2>7: dish-=1
                if dish==14: dish=0
                self.dishes[dish].n+=1 # drop one ball
                self.n-=1
            if self.n==0:
                g.state=1
                if dish==0:
                    self.dishes[0].orange=True
                    g.state=4
                elif self.dishes[dish].n==1 and dish>7:
                    opp=14-dish; n=self.dishes[opp].n
                    if n>0:
                        self.move(1,self.group2,15); self.dishes[dish].n=0
                        self.dishes[opp].n=0
                        self.move(n,opp,0)
                        self.dishes[dish].green=True; self.dishes[opp].green=True
                        self.n=n+1
                        g.state=6
                self.complete()
            else:
                self.group1=self.group2; self.group2+=1
                if self.group2==16: self.group2=0
                self.move(self.n,self.group1,self.group2)

    def complete(self):
        if g.state==7: return True
        w=self.dishes[0].n; p=self.dishes[7].n
        if p>24: g.player+=1; g.state=7; return True
        if w>24: g.wizard+=1; g.state=8; return True
        if w==24 and p==24: g.state=9; return True
        return False

    def player_ok(self):
        for dish in range(1,7):
            if self.dishes[dish].n>0: return True
        return False
    
    def wizard_ok(self):
        for dish in range(8,14):
            if self.dishes[dish].n>0: return True
        return False
    
        
    
