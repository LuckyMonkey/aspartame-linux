# load_save.py
import g

loaded = []  # list of strings


def load(f):
    global loaded
    try:
        for line in f.readlines():
            loaded.append(line)
    except BaseException:
        pass


def save(f):
    f.write(str(g.count) + '\n')

# note need for rstrip() on strings


def retrieve():
    global loaded
    if len(loaded) > 0:
        g.count = int(loaded[0])
