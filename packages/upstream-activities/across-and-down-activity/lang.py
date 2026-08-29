import os,random

filehandle=[None]*10

# checks word (2 to 9 letters) -> True/False
def check_word(w):
    l=len(w)
    if l<2 or l>9: return False
    fname=os.path.join('data',str(l)+'.txt')
    f=filehandle[l]
    if f==None: f=open(fname,'r'); filehandle[l]=f
    p1=0; p2=int(os.path.getsize(fname)/(l+2))
    w0=w.lower()
    while True:
        q1=p1; q2=p2
        p=int((p1+p2)/2)
        f.seek(p*(l+2))
        w1=f.read(l)
        if w0==w1: return True
        if w0<w1: p2=p
        else: p1=p
        if (q1==p1) and (q2==p2): return False
    
letters='EEEEEEEEEEEEAAAAAAAAAIIIIIIIIIOOOOOOOONNNNNNRRRRRRTTTTTT\
LLLLSSSSUUUUDDDDGGGBBCCMMPPFFHHVVWWYYKJXQZ'.lower()

def letter():
    r=random.randint(0,len(letters)-1)
    return letters[r]

def vowel():
    l='x'
    while l not in 'aeiou': l=letter()
    return l

def consonant():
    l='a'
    while l in 'aeiou': l=letter()
    return l

    
    
    

