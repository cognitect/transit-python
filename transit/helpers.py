import itertools

## Copyright (c) Cognitect, Inc.
## All rights reserved.

def mapcat(f, i):
    return itertools.chain.from_iterable(itertools.imap(f, i))

def pairs(i):
    return zip(*[iter(i)] * 2)

cycle = itertools.cycle

def take(n, i):
    return itertools.islice(i, 0, n)

