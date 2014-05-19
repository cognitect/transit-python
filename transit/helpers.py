import itertools



def mapcat(f, seq):
    for x in seq:
        for y in f(x):
            yield y

def pairs(i):
    for x in range(0, len(i), 2):
        yield (i[x], i[x+1])

def cycle(x):
    d = tuple(x)
    while True:
        for x in d:
            yield x

def take(n, s):
    c = 0
    for x in s:
        yield x
        c += 1
        if c >= n:
            break