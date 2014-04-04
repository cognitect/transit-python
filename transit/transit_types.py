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


class Set(collections.Set, set):
    def __init__(self, itms):
        self.itms = itms

    def __iter__(self):
        return self.itms.__iter__()

    def __contains__(self, item):
        return item in self.itms

    def __len__(self):
        return len(self.itms)

    def __le__(self, other):
        return self == other

    def __eq__(self, other):
        if not (isinstance(other, Set) or isinstance(other, set)):
            return False

        if not len(self) == len(other):
            return False

        for x in other:
            if x not in self:
                return False

        return True

class Dict(dict):
    def __hash__(self):
        h = reduce(lambda x, y: hash(x) ^ hash(y), self.keys(), 0)
        h = reduce(lambda x, y: hash(x) ^ hash(y), self.values(), h)
        return h

class Vector(list):
    def __hash__(self):
        h = reduce(lambda x, y: hash(x) ^ hash(y), self, 1)
        return h

