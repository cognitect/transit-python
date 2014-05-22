# Copyright (c) Cognitect, Inc.
# All rights reserved.

import re

FIRST_ORD = 33
CACHE_SIZE = 94
MIN_SIZE_CACHEABLE = 4
ESCAPED = re.compile("^~(#|\$|:)")
## Copyright (c) Cognitect, Inc.
## All rights reserved.

def is_cache_key(name):
    return len(name) > 0 and name[0] == "^"

def encode_key(i):
    return "^" + chr(i + FIRST_ORD)

def decode_key(s):
    return ord(s[1]) - FIRST_ORD


def is_cacheable(string, as_map_key=False):
    return string and len(string) >= MIN_SIZE_CACHEABLE and (as_map_key or ESCAPED.match(string))

class RollingCache(object):


    def __init__(self):
        self.clear()

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
        return self.size() > CACHE_SIZE


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
        self.key_to_value = {}
        self.value_to_key = {}



