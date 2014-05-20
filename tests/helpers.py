from transit.transit_types import Symbol, Keyword, frozendict
from transit.helpers import cycle, take, pairs
from itertools import izip

def ints_centered_on(m, n=5):
    return tuple(range(m - n, m + n + 1))


def array_of_symbools(m, n=None):
    if n is None:
        n = m

    seeds = map(lambda x: Keyword("key"+str(x).zfill(4)), range(0, m))
    return take(n, cycle(seeds))


def hash_of_size(n):
    return frozendict(izip(array_of_symbools(n), range(0, n+1)))