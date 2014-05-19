
def ints_centered_on(m, n=5):
    return tuple(range(m - n, m + n + 1))

def mapcat(f, seq):
    for x in seq:
        for y in f(x):
            yield y