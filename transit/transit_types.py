import collections

class Keyword(object):
    def __init__(self, value):
        assert isinstance(value, str)
        self.str = value

    def __eq__(self, other):
        return self is other

    def __call__(self, mp):
        return mp[self]

    def __repr__(self):
        return ":" + self.str

    def __str__(self):
        return ":" + self.str

class Symbol(object):
    def __init__(self, value):
        assert isinstance(value, str)
        self.str = value

    def __eq__(self, other):
        assert isinstance(other, Symbol)
        return self.str == other.str

    def __call__(self, mp):
        return mp[self]

    def __repr__(self):
        return self.str

    def __str__(self):
        return self.str

kw_cache = {}

class _KWS(object):
    def __getattr__(self, item):
        value = self(item)
        setattr(self, item, value)
        return value

    def __call__(self, str):
        if str in kw_cache:
            return kw_cache[str]
        else:
            kw_cache[str] = Keyword(str)
            return kw_cache[str]

kws = _KWS()


class Set(set):
    def __hash__(self):
        return reduce(lambda x, y: hash(x) ^ hash(y), self, 0)


class Dict(dict):
    def __hash__(self):
        h = reduce(lambda x, y: hash(x) ^ hash(y), self.keys(), 0)
        h = reduce(lambda x, y: hash(x) ^ hash(y), self.values(), h)
        return h

class Vector(list):
    def __hash__(self):
        h = reduce(lambda x, y: hash(x) ^ hash(y), self, 1)
        return h

