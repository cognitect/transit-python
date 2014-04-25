## Copyright (c) Cognitect, Inc.
## All rights reserved.

import collections

class Keyword(object):
    def __init__(self, value):
        assert isinstance(value, str)
        self.str = value

    def __hash__(self):
        return hash(self.str)

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

    def __hash__(self):
        return hash(self.str)

    def __eq__(self, other):
        assert isinstance(other, Symbol)
        return self.str == other.str

    def __ne__(self, other):
        return not self == other

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

class TaggedData(object):
    def __init__(self, tag, data):
        self.tag = tag
        self.data = data
    def __eq__(self, other):
        if isinstance(other, TaggedData):
            return self.tag == other.tag and \
                   self.data == other.data
        return False

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return reduce(lambda a, b: hash(a) ^ hash(b), self.data, 0)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "#"+self.tag + repr(self.data)

class Set(TaggedData):
    def __init__(self, data):
        TaggedData.__init__(self, "set", data)

class CMap(TaggedData):
    def __init__(self, data):
        TaggedData.__init__(self, "cmap", data)

class Vector(TaggedData):
    def __init__(self, data):
        TaggedData.__init__(self, "vector", data)

class Array(TaggedData):
    def __init__(self, data):
        TaggedData.__init__(self, "array", data)

class List(TaggedData):
    def __init__(self, data):
        TaggedData.__init__(self, "list", data)

class URI(TaggedData):
    def __init__(self, data):
        TaggedData.__init__(self, "uri", data)