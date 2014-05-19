# Copyright (c) Cognitect, Inc.
# All rights reserved.

import transit_types
from transit_types import TaggedValue
from constants import *
import uuid
import re
import ctypes
import dateutil.parser
import datetime
import dateutil.tz

from rolling_cache import RollingCache, is_cacheable, is_cache_key

def identity(x):
    return x

def to_uuid(x):
    if isinstance(x, (unicode, str)):
        return uuid.UUID(x)

    # hack to remove signs
    a = ctypes.c_ulong(x[0])
    b = ctypes.c_ulong(x[1])
    combined = a.value << 64 | b.value
    return uuid.UUID(int=combined)

def to_date(x):
    if isinstance(x, (long, int)):
        return datetime.datetime.fromtimestamp(x / 1000.0, dateutil.tz.tzutc())
    return dateutil.parser.parse(x)

default_options = {"decoders": {"_": lambda _: None,
                                ":": transit_types.Keyword,
                                "$": transit_types.Symbol,
                                "?": lambda x: x == "t",
                                "i": int,
                                "f": float,
                                "u": to_uuid,
                                "r": transit_types.URI,
                                "t": to_date,
                                "list": identity,
                                "set": frozenset,
                                "'": identity},
                   "default_string_decoder": lambda x: "`" + str(x),
                   "default_hash_decoder": lambda h: TaggedValue(h.keys()[0], h.values()[0]), }

ESC_re = re.compile("^" + ESC)
TAG_re = re.compile("^" + TAG)

class Decoder(object):

    def __init__(self, options={}):
        self.options = default_options.copy()
        self.options.update(options)

        self.decoders = self.options["decoders"]

    def decode(self, node, cache=None, as_map_key=False):
        if not cache:
            cache = RollingCache()
        return self._decode(node, cache, as_map_key)

    def _decode(self, node, cache, as_map_key):
        tp = type(node)
        if tp is str:
            return self.decode_string(unicode(node, "utf-8"), cache, as_map_key)
        if tp is unicode:
            return self.decode_string(node, cache, as_map_key)
        elif tp is dict:
            return self.decode_hash(node, cache, as_map_key)
        elif tp is list:
            return tuple(map(lambda x: self._decode(x, cache, as_map_key), node))
        else:
            return node

    def decode_string(self, string, cache, as_map_key):
        if is_cacheable(string, as_map_key):
            cache.encode(string, as_map_key)
            return self.parse_string(string, cache, as_map_key)
        elif is_cache_key(string):
            return self._decode(cache.decode(string, as_map_key), cache, as_map_key)
        else:
            return self.parse_string(string, cache, as_map_key)

    def decode_hash(self, hash, cache, as_map_key):
        if len(hash) == 1:
            key = self._decode(hash.keys()[0], cache, True)
            if isinstance(key, (str, unicode)) and TAG_re.match(key):
                decoder = self.decoders.get(key[2:], None)
                if decoder:
                    return decoder(self._decode(hash.values()[0], cache, as_map_key))
                else:
                    return self.options["default_hash_decoder"]({key: self.decode(hash.values()[0], cache, False)})
            else:
                return {key: self._decode(hash.values()[0], cache, False)}
        else:
            h = {}
            for k, v in hash.items():
                h[self._decode(k, cache, True)] = self._decode(v, cache, False)
            return transit_types.frozendict(h)



    def parse_string(self, string, cache, as_map_key):
        if ESC_re.match(string):
            m = string[1]
            if m == ESC or m == SUB or m == RES:
                return string[1:]
            elif m == "#":
                return string
            else:
                decoder = self.decoders.get(string[1])
                if decoder:
                    return decoder(string[2:])
                else:
                    return self.options["default_string_decoder"](string)
        else:
            return string
