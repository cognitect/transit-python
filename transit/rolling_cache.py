# Copyright (c) Cognitect, Inc.
# All rights reserved.

import re

FIRST_ORD = 33
CACHE_SIZE = 94
MIN_SIZE_CACHEABLE = 4
ESCAPED = re.compile("^~(#|\$|:)")

def is_cache_key(name):
    return name[0] == "^"

def encode_key(i):
    return "^#" + str(i + FIRST_ORD)

def decode_key(s):
    return ord(s[1]) - FIRST_ORD

def is_cacheable(str, as_map_key=False):
    return str and len(str) >= MIN_SIZE_CACHEABLE and (as_map_key or ESCAPED.match(str))

class RollingCache(object):


    def __init__(self):
        self.clear()

    def decode(self, name, as_map_key=False):
        """Always returns the name"""
        key = self.value_to_key.get(name, None)
        if key is not None:
            return key
        return self.encache(name) if is_cacheable(name, as_map_key) else name


    def encode(self, name, as_map_key=False):
        """Returns the name the first time and the key after that"""
        key = self.key_to_value.get(name, None)
        if key is not None:
            return key
        return self.encache(name) if is_cacheable(name, as_map_key) else name


    def size(self):
        return len(self.key_to_value)

    def is_cache_full(self):
        return self.size() >= CACHE_SIZE


    def encache(self, name):
        if self.is_cache_full():
            self.clear()

        existing_key = self.value_to_key.get(name, None)
        if existing_key is not None:
            return existing_key

        key = encode_key(len(self.key_to_value))
        self.key_to_value[key] = name
        self.value_to_key[name] = key

        return name


    def clear(self):
        self.key_to_value = {}
        self.value_to_key = {}



