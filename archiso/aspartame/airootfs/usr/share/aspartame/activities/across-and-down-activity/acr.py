#acr.py
import g,utils,pygame,lang,random

# x centre, y bottom
letters_c=[(600,71),(732,82),(856,114),(965,165),(1053,233),(1114,313),(1146,374),(1146,491),(1114,579),(1053,659),(965,727),(856,778),(732,810),(600,821),(468,810),(344,778),(235,727),(147,659),(86,579),(54,491),(54,401),(86,313),(147,233),(235,165),(344,114),(468,82)]
scores=[('aeilnorstu',1),('bcdgmp',2),('fhkvwy',4),('jqxz',8)]
class AZ:
    def __init__(self,l,x1,y1,x2,y2):
        self.l=l; self.x1=x1; self.y1=y1; self.x2=x2; self.y2=y2

class Cell:
    def __init__(self,x,y,r,c,ind):
        self.x=x; self.y=y; self.r=r; self.c=c; self.ind=ind
        self.sl=None; self.l=None; self.fixed=False

class Acr:
    def __init__(self):
        # grid letters
        img=utils.load_image('abcd.png',True)
        img_score=utils.load_image('abcd_score.png',True)
        wf=0.0+img.get_width()/26.0; self.h=img.get_height()
        x=0.0; y=0; self.w=int(wf)
        self.imgs=[]; self.imgs_score=[]
        for i in range(26):
            self.imgs.append(img.subsurface((int(x+.5),y,self.w,self.h)))
            self.imgs_score.append(img_score.subsurface((int(x+.5),y,self.w,self.h)))
            x+=wf
        # oval letters
        self.azs=[]
        s=g.sy(1.1); dx=g.x0; dy=g.sy(.5)
        for ind in range(26):
            l=chr(ind+97)
            x,y=letters_c[ind]
            y2=int(g.imgf*y+g.sy(.1)+.5); y1=y2-s-s
            if l in 'bdfhkl': y1-=dy
            if l in 'gjpqy': y2+=dy
            x=int(g.imgf*x+dx+.5); 
            az=AZ(l,x-s,y1,x+s,y2)
            self.azs.append(az)
        # grid cells
        self.cells=[]
        s=g.sy(14.4)/9; x0=g.sx(16)-s*4.5; y0=g.sy(11.15)-s*4.5
        y=y0; ind=0
        for r in range(9):
            x=x0
            for c in range(9):
                cell=Cell(int(x+.5),int(y+.5),r,c,ind)
                self.cells.append(cell)
                x+=s; ind+=1
            y+=s
        self.side=int(s+.5)
        self.setup()

    def setup(self):
        self.green=40
        self.message=None
        self.first=True
        for cell in self.cells:
            cell.fixed=False; cell.l=None; cell.sl=None
        k=0; g.target=0
        while k<12:
            ind=random.randint(0,80)
            cell=self.cells[ind]
            if cell.r>0 and cell.r<8 and cell.c>0 and cell.c<8:
                if cell.sl==None:
                    if not self.neighbours(cell):
                        cell.sl=lang.letter(); g.target+=self.score(cell.sl)
                        k+=1
        g.score=0; self.glow=[]; g.percent='= 0%'; g.complete=False

    def update(self):
        if self.glow==[]: return
        d=pygame.time.get_ticks()-g.ms
        if d>500: # delay in ms
            self.glow=[]
            g.redraw=True
                    
    def replay(self):
        for cell in self.cells: cell.fixed=False; cell.l=None
        g.score=0; self.glow=[]; self.first=True; g.percent='= 0%'

    def draw(self):
        s=self.side+1; gy=70; sx=int(self.side/2); sy=sx+g.sy(.08)
        for cell in self.cells:
            x,y=cell.x,cell.y
            colr=(225,255,255)
            if cell.fixed: colr=(255,220,220)
            pygame.draw.rect(g.screen,colr,(x,y,s,s))
            pygame.draw.rect(g.screen,(gy,gy,gy),(x,y,s,s),1)
            if cell.l != None:
                ind=ord(cell.l)-97
                utils.centre_blit(g.screen,self.imgs[ind],(x+sx,y+sy))
            elif cell.sl != None:
                ind=ord(cell.sl)-97
                utils.centre_blit(g.screen,self.imgs_score[ind],(x+sx,y+sy))
        cell=self.cells[self.green]; x,y=cell.x,cell.y
        pygame.draw.rect(g.screen,utils.RED,(x-1,y-1,s+2,s+2),5)
        for cell in self.glow:
            x,y=cell.x,cell.y; w2=self.side/2; x+=w2; y+=w2
            utils.centre_blit(g.screen,g.glow,(x,y))

    def do_letter(self,l):
        cell=self.cells[self.green]
        if cell.fixed: return
        if l==' ': cell.l=None; return
        if l>='a' and l<='z': cell.l=l
        
    def which_oval(self):
        for ind in range(26):
            az=self.azs[ind]
            if utils.mouse_in(az.x1,az.y1,az.x2,az.y2): return az.l
        return None

    def which_cell(self):
        s=self.side
        for cell in self.cells:
            x,y=cell.x,cell.y
            if utils.mouse_in(x,y,x+s,y+s): return cell
        return None

    def left(self):
        ind=self.green; cell=self.cells[ind]
        if cell.c==0: ind+=8
        else: ind-=1
        self.green=ind
        
    def right(self):
        ind=self.green; cell=self.cells[ind]
        if cell.c==8: ind-=8
        else: ind+=1
        self.green=ind
        
    def up(self):
        ind=self.green; cell=self.cells[ind]
        if cell.r==0: ind+=72
        else: ind-=9
        self.green=ind
        
    def down(self):
        ind=self.green; cell=self.cells[ind]
        if cell.r==8: ind-=72
        else: ind+=9
        self.green=ind

    def cell1(self,r,c):
        ind=r*9+c; return self.cells[ind]
        
    def fix_all(self):
        self.glow=[]
        for cell in self.cells:
            if cell.l!=None and not cell.fixed:
                if cell.sl!=None:
                    if cell.l==cell.sl:
                        g.score+=self.score(cell.l); self.glow.append(cell)
                        g.ms=pygame.time.get_ticks()
                cell.fixed=True
        percent=int(100.0*g.score/g.target+.5)
        g.percent='= '+str(percent)+'%'
        if percent>g.best: g.best=percent
        if percent==100:
            if not g.complete: g.count+=1; g.complete=True
            
    def clear(self):
        for cell in self.cells:
            if not cell.fixed: cell.l=None
            
    def neighbours(self,cell):
        r,c=cell.r,cell.c
        if r>0:
            if self.cell1(r-1,c).sl!=None: return True
        if r<8:
            if self.cell1(r+1,c).sl!=None: return True
        if c>0:
            if self.cell1(r,c-1).sl!=None: return True
        if c<8:
            if self.cell1(r,c+1).sl!=None: return True
        return False
    
    def score(self,l):
        for ind in range(4):
            letters,score=scores[ind]
            if l in letters: return score
        return 0

    def check(self):
        self.message=None
        # find min & max row & col for new letters
        rmin=100; rmax=-1; cmin=100; cmax=-1
        for cell in self.cells:
            if cell.l!=None and not cell.fixed:
                r,c=cell.r,cell.c
                if r<rmin: rmin=r
                if r>rmax: rmax=r
                if c<cmin: cmin=c
                if c>cmax: cmax=c
        if rmin==100:
            self.message='please enter a new letter'; return False
        if (rmax-rmin)>0 and (cmax-cmin)>0:
            self.message='your letters must be in a single row or column'; return False
        self.connected=False; self.len=0
        for r in range(rmin,rmax+1):
            cell_list=[]
            for c in range(9):
                cell_list.append(self.cell1(r,c))
            if not self.check_rc(cell_list): return False
        for c in range(cmin,cmax+1):
            cell_list=[]
            for r in range(9):
                cell_list.append(self.cell1(r,c))
            if not self.check_rc(cell_list): return False
        if self.len==1:
            self.message='please enter another letter'; return False
        if not self.first and not self.connected:
            self.message='letters must be connected'; return False
        # all ok
        self.fix_all()
        self.first=False
        return True

    def check_rc(self,cell_list):
        fxd=False; ltr=False; done=False; word=''
        for cell in cell_list:
            if cell.fixed:
                if not done: fxd=True; word+=cell.l
            elif cell.l!=None:
                if not done:
                    ltr=True; word+=cell.l
                else:
                    self.message='your letters must be together'
                    return False
            else: # must be empty
                if ltr: done=True
                else: fxd=False; word=''
        if not ltr: return True # no new letters so ignore
        if len(word)>self.len: self.len=len(word)
        if len(word)==1: return True
        if fxd: self.connected=True
        if not lang.check_word(word):
            self.message='sorry, '+word+' is not in my list'
            return False
        return True
        
        
    
