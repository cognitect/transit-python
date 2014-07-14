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

from constants import ESC, SUB, MAP_AS_ARR

FIRST_ORD = 48
CACHE_CODE_DIGITS = 44
CACHE_SIZE = CACHE_CODE_DIGITS * CACHE_CODE_DIGITS
MIN_SIZE_CACHEABLE = 4

def is_cache_key(name):
    return len(name) and (name[0] == SUB and name != MAP_AS_ARR)

def encode_key(i):
    lo = i % CACHE_CODE_DIGITS
    hi = i // CACHE_CODE_DIGITS
    if hi == 0:
        return "^" + chr(i + FIRST_ORD)
    return "^" + chr(hi + FIRST_ORD) + chr(lo + FIRST_ORD)

def decode_key(s):
    sz = len(s)
    if sz == 2:
        return ord(s[1]) - FIRST_ORD
    return (ord(s[2]) - FIRST_ORD) + (CACHE_CODE_DIGITS * (ord(s[1]) - FIRST_ORD))

def is_cacheable(string, as_map_key=False):
    return string \
            and len(string) >= MIN_SIZE_CACHEABLE \
            and (as_map_key \
            or (string[:2] in ["~#", "~$", "~:"]))

class RollingCache(object):
    """ This is the internal cache used by python-transit for cacheing and
    expanding map keys during writing and reading.  The cache enables transit
    to minimize the amount of duplicate data sent over the wire, effectively
    compressing down the overall payload size.  The cache is not intended to
    be used directly."""
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

