# ah.py
import g,random,utils,pygame

squares=[] # nr x nc - surrounded by "illegals"
colours=[(0,0,0),(255,255,0),(0,255,0),(0,0,255),(255,0,255)]
RC=[None,(5,7),(6,9),(7,11),(8,12),(9,14),(10,15),(11,17),(12,19),(13,20)]
  # level 1 to 9

class Square:
    def __init__(self, ind, r, c, x, y, N, S, E, W):
        self.ind=ind; self.r=r; self.c=c; self.x=x; self.y=y
        self.N=N; self.S=S; self.E=E; self.W=W #  indexes
        self.group=-1 # -1 outside 0 unassigned 1...
        self.colour=0; # 0,1,2,3,4
        
class Grid:
    def __init__(self):
        self.clash_rects=[]

    def new1(self): # called when nr & nc changed
        global squares
        nr,nc=RC[g.level]
        self.total=(nr+2)*(nc+2)
        self.d=0.0+g.sy(18)/nr
        w=nc*self.d; x0=(g.w-w-g.sx(2.7))/2
        y0=g.sy(.5)
        squares=[]
        y=y0; ind=0
        for r in range(nr+2):
            x=x0
            for c in range(nc+2):
                N=ind-nc-2; W=ind-1; S=ind+nc+2; E=ind+1
                sq=Square(ind,r,c,x,y,N,S,E,W); squares.append(sq)
                if c>0 and c<=nc:
                    if r>0 and r<=nr: sq.group=0
                    x+=self.d
                ind+=1
            if r>0: y+=self.d
        self.nr=nr; self.nc=nc

    def setup(self):
        self.colour_ind=0
        for sq in squares:
            if sq.group>-1: sq.group=0; sq.colour=0
        self.ng=int(self.total/12)
        for gp in range(self.ng):
            sq=self.empty_sq()
            if sq!=None: self.make_group(sq,gp)
            else: break
        # assign unallocated squares
        for i in range(10000):
            unchanged=True
            for sq0 in squares:
                if sq0.group==0:
                    gp=0; unchanged=False
                    if squares[sq0.N].group>0: gp=squares[sq0.N].group
                    elif squares[sq0.S].group>0: gp=squares[sq0.S].group
                    elif squares[sq0.E].group>0: gp=squares[sq0.E].group
                    elif squares[sq0.W].group>0: gp=squares[sq0.W].group
                    sq0.group=gp
            if unchanged: break
        self.fill_in_singles()
        self.clash_rects=[]; self.finished=False; g.scored=False
                
    def reset(self):
        self.colour_ind=0
        for sq in squares:
            if sq.group>-1: sq.colour=0
        self.clash_rects=[]; self.finished=False

    def empty_sq(self):
        for i in range(1000):
            ind=random.randint(1,self.total-1)
            sq=squares[ind]
            if sq.group==0: return sq
        return None

    def make_group(self, sq0, gp): # start @ sq0 -> group, gp
        sq=sq0
        for i in range(int(self.total/self.ng)):
            sq.group=gp
            mates=[sq.N,sq.S,sq.E,sq.W]
            rnd=random.randint(0,3); ind=mates[rnd]
            t=squares[ind]
            if t.group==0: sq=t
            
    def fill_in_singles(self):
        for sq in squares:
            gp=sq.group
            if gp>-1:
                k=0
                ng=squares[sq.N].group; sg=squares[sq.S].group
                eg=squares[sq.E].group; wg=squares[sq.W].group
                if ng==-1 or ng!=gp: k+=1
                if sg==-1 or sg!=gp: k+=1
                if eg==-1 or eg!=gp: k+=1
                if wg==-1 or wg!=gp: k+=1
                if k==4:
                    if ng!=-1: ngp=ng
                    if sg!=-1: ngp=sg
                    if eg!=-1: ngp=eg
                    if wg!=-1: ngp=wg
                    sq.group=ngp 

    def draw(self):
        d=self.d; d+=2
        for sq in squares:
            if sq.group>-1:
                pygame.draw.rect(g.screen,colours[sq.colour],(sq.x,sq.y,d,d))
                cxy=(sq.x+self.d/2,sq.y+self.d/2)
                #utils.display_number(sq.group,cxy,g.font1,(255,255,255))
        for rect in self.clash_rects:
            pygame.draw.rect(g.screen,utils.RED,rect)
        self.lines()

    def lines(self):
        grey=200; colour=(grey,grey,grey); w=4
        for sq0 in squares:
            if sq0.r>0 and sq0.c>0:
                gp=sq0.group
                sq=squares[sq0.N]
                if sq.group!=gp:
                    pygame.draw.line(g.screen,colour,\
                                     (sq0.x,sq0.y),(sq0.x+self.d,sq0.y),w)
                sq=squares[sq0.W]
                if sq.group!=gp:
                    pygame.draw.line(g.screen,colour,\
                                     (sq0.x,sq0.y),(sq0.x,sq0.y+self.d),w)
    def clashes(self):
        self.clash_rects=[]
        d=self.d; d+=2; dd=g.sy(.5)
        # vertical
        for sq0 in squares:
            r=sq0.r; c=sq0.c
            if r>0 and c>0 and r<=self.nr and c<self.nc:
                sq=squares[sq0.E]
                if sq0.colour>0:
                    if sq0.group!=sq.group:
                        if sq0.colour==sq.colour: #clash
                            x=sq.x-dd; y=sq.y
                            self.clash_rects.append((x,y,dd*2,d))
        # horizontal
        for sq0 in squares:
            r=sq0.r; c=sq0.c
            if r>0 and c>0 and r<self.nr and c<=self.nc:
                sq=squares[sq0.S]
                if sq0.colour>0:
                    if sq0.group!=sq.group:
                        if sq0.colour==sq.colour: #clash
                            x=sq.x; y=sq.y-dd
                            self.clash_rects.append((x,y,d,dd*2))

    def which(self):
        for sq in squares:
            if sq.group!=-1:
                if utils.mouse_in(sq.x,sq.y,sq.x+self.d,sq.y+self.d):
                    return sq
        return None

    def click(self):
        if self.complete(): return False
        sq=self.which()
        if sq!=None:
            k=self.colour_ind
            if sq.colour==k: self.colour_ind=0
            self.colour_in(sq); self.clashes()
            self.colour_ind=k
            return True
        return False

    def colour_in(self, sq0):
        gp=sq0.group
        for sq in squares:
            if sq.group==gp: sq.colour=self.colour_ind

    def complete(self):
        if self.finished: return True
        for sq in squares:
            if sq.group!=-1:
                if sq.colour==0: return False
        if len(self.clash_rects)>0: return False
        if not g.scored: g.score+=g.level
        g.scored=True
        self.finished=True
        return True

        


                    
