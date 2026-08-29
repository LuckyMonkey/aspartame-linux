#load_save.py
import g

loaded=[] # list of strings

def load(f):
    global loaded
    try:
        for line in f.readlines():
            loaded.append(line)
    except:
        pass

def save(f):
    f.write(str(g.player)+'\n')
    f.write(str(g.wizard)+'\n')

def retrieve():
    global loaded
    if len(loaded)>1:
        g.player=int(loaded[0])
        g.wizard=int(loaded[1])


    
