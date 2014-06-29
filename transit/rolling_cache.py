# Copyright (c) Cognitect, Inc.
# All rights reserved.
import re
from constants import ESC, SUB, MAP_AS_ARR

FIRST_ORD = 33
CACHE_SIZE = 94*94
MIN_SIZE_CACHEABLE = 4
ESCAPED = re.compile("^~(#|\$|:)")

def is_cache_key(name):
    return len(name) and (name[0] == SUB and name != MAP_AS_ARR)

def encode_key(i):
    lo = i % 94
    hi = i // 94
    if hi == 0:
        return "^" + chr(i + FIRST_ORD)
    return "^" + chr(hi + FIRST_ORD) + chr(lo + FIRST_ORD)

def decode_key(s):
    sz = len(s)
    if sz == 2:
        return ord(s[1]) - FIRST_ORD
    return (ord(s[2]) - FIRST_ORD) + (94 * (ord(s[1]) - FIRST_ORD))

def is_cacheable(string, as_map_key=False):
    return string \
            and len(string) >= MIN_SIZE_CACHEABLE \
            and (as_map_key \
            #or string[0] == ESC) # TODO: The docs suggest a robust check here, but not sure if that's needed?
            or ESCAPED.match(string))

class RollingCache(object):
    # (1) should we use list or dict on read side? ##- probably dictionary is best for lookup by code.
      # dict lookup should be amortized O(1), for list O(n)
    # (2) currently stores value read from the wire, should probably store value after decoding
    # so we don't do multiple decodes. Sped up parsing in ruby by 30%.
    def __init__(self):
        self.key_to_value = {}
        self.value_to_key = {}

    # if index rolls over... (bug)
    def decode(self, name, as_map_key=False):
        """Always returns the name"""
        if is_cache_key(name) and (name in self.key_to_value):
            return self.key_to_value[name]
        return self.encache(name) if is_cacheable(name, as_map_key) else name

    def encode(self, name, as_map_key=False):
        """Returns the name the first time and the key after that"""
        if name in self.key_to_value:
            return self.key_to_value[name]
        return self.encache(name) if is_cacheable(name, as_map_key) else name

    def size(self):
        return len(self.key_to_value)

    def is_cache_full(self):
        return len(self.key_to_value) > CACHE_SIZE

    def encache(self, name):
        if self.is_cache_full():
            self.clear()
        elif name in self.value_to_key:
            return self.value_to_key[name]

        key = encode_key(len(self.key_to_value))
        self.key_to_value[key] = name
        self.value_to_key[name] = key

        return name

    def clear(self):
        self.value_to_key = {}

