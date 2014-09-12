## Copyright 2014 Cognitect. All Rights Reserved.
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS-IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

import collections

class Keyword(object):
    def __init__(self, value):
        assert isinstance(value, basestring)
        self.str = value
        self.hv = value.__hash__()

    def __hash__(self):
        return self.hv

    def __eq__(self, other):
        return isinstance(other, Keyword) and self.str == other.str

    def __call__(self, mp):
        return mp[self] # Maybe this should be .get()

    def __repr__(self):
        return "<Keyword " + self.str + ">"

    def __str__(self):
        return self.str

class Symbol(object):
    def __init__(self, value):
        assert isinstance(value, basestring)
        self.str = value
        self.hv = value.__hash__()

    def __hash__(self):
        return self.hv

    def __eq__(self, other):
        return isinstance(other, Symbol) and self.str == other.str

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

class TaggedValue(object):
    def __init__(self, tag, rep):
        self.tag = tag
        self.rep = rep
    def __eq__(self, other):
        if isinstance(other, TaggedValue):
            return self.tag == other.tag and \
                   self.rep == other.rep
        return False

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        if isinstance(self.rep, list):
            return reduce(lambda a, b: hash(a) ^ hash(b), self.rep, 0)
        return hash(self.rep)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return self.tag + " " + repr(self.rep)

class Set(TaggedValue):
    def __init__(self, rep):
        TaggedValue.__init__(self, "set", rep)

class CMap(TaggedValue):
    def __init__(self, rep):
        TaggedValue.__init__(self, "cmap", rep)

class Vector(TaggedValue):
    def __init__(self, rep):
        TaggedValue.__init__(self, "vector", rep)

class Array(TaggedValue):
    def __init__(self, rep):
        TaggedValue.__init__(self, "array", rep)

class List(TaggedValue):
    def __init__(self, rep):
        TaggedValue.__init__(self, "list", rep)

class URI(TaggedValue):
    def __init__(self, rep):
        TaggedValue.__init__(self, "uri", rep)

from collections import Mapping, Hashable, namedtuple
class frozendict(Mapping, Hashable):
    def __init__(self, *args, **kwargs):
        self._dict = dict(*args, **kwargs)
    def __len__(self):
        return len(self._dict)
    def __iter__(self):
        return iter(self._dict)
    def __getitem__(self, key):
        return self._dict[key]
    def __hash__(self):
        return hash(frozenset(self._dict.items()))
    def __repr__(self):
        return 'frozendict(%r)' % (self._dict,)

class Link(object):
    # Class property constants for rendering types
    LINK = u"link"
    IMAGE = u"image"

    # Class property constants for keywords/obj properties.
    HREF = u"href"
    REL = u"rel"
    PROMPT = u"prompt"
    NAME = u"name"
    RENDER = u"render"

    def __init__(self, href=None, rel=None, name=None, render=None, prompt=None):
        self._dict = frozendict()
        assert href and rel
        if render:
            assert render.lower() in [Link.LINK, Link.IMAGE]
        self._dict = {Link.HREF: href,
                      Link.REL: rel,
                      Link.NAME: name,
                      Link.RENDER: render,
                      Link.PROMPT: prompt}

    def __eq__(self, other):
        return self._dict == other._dict
    def __ne__(self, other):
        return self._dict != other._dict

    @property
    def href(self):
        return self._dict[Link.HREF]
    @property
    def rel(self):
        return self._dict[Link.REL]
    @property
    def prompt(self):
        return self._dict[Link.PROMPT]
    @property
    def name(self):
        return self._dict[Link.NAME]
    @property
    def render(self):
        return self._dict[Link.RENDER]
    @property
    def as_map(self):
        return self._dict
    @property
    def as_array(self):
        return [self.href, self.rel, self.name, self.render, self.prompt]

class Boolean(object):
    """To allow a separate t/f that don't hash as 1/0. Don't call this directly.
    Note that the Booleans are for preserving hash/set bools that duplicate 1/0
    and not designed for use in Python. You can get a Python bool using bool(x)
    where x is true or false.
    """
    def __init__(self, name):
        self.v = True if name == "true" else False
        self.name = name

    def __nonzero__(self):
        return self.v

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

# lowercase rep matches java/clojure
false = Boolean("false")
true = Boolean("true")
