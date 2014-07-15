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

import transit_types
from constants import *
from collections import OrderedDict
from helpers import pairs
import read_handlers as rh
from rolling_cache import RollingCache, is_cacheable, is_cache_key

class Tag(object):
    def __init__(self, tag):
        self.tag = tag

default_options = {"decoders": {"_": rh.NoneHandler,
                                ":": rh.KeywordHandler,
                                "$": rh.SymbolHandler,
                                "?": rh.BooleanHandler,
                                "i": rh.IntHandler,
                                "f": rh.FloatHandler,
                                "u": rh.UuidHandler,
                                "r": rh.UriHandler,
                                "t": rh.DateHandler,
                                "m": rh.DateHandler,
                                "n": rh.BigIntegerHandler,
                                "link": rh.LinkHandler,
                                "list": rh.ListHandler,
                                "set": rh.SetHandler,
                                "cmap": rh.CmapHandler,
                                "'": rh.IdentityHandler},
                   "default_decoder": rh.DefaultHandler}

ground_decoders = {"_": rh.NoneHandler,
                   "?": rh.KeywordHandler,
                   "i": rh.IntHandler,
                   "'": rh.IdentityHandler}

class Decoder(object):
    """ The Decoder is the lowest level entry point for parsing, decoding, and
    fully converting Transit data into Python objects.

    During the creation of a Decoder object, you can specify custom options
    in a dictionary.  One such option is 'decoders'.  Note that while you
    can specify your own decoders and override many of the built in decoders,
    some decoders are silently enforced and cannot be overriden.  These are
    known as Ground Decoders, and are needed to maintain bottom-tier
    compatibility."""

    def __init__(self, options={}):
        self.options = default_options.copy()
        self.options.update(options)

        self.decoders = self.options["decoders"]
        # Always ensure we control the ground decoders
        self.decoders.update(ground_decoders)

    def decode(self, node, cache=None, as_map_key=False):
        """ Given a node of data (any supported decodeable obj - string, dict,
        list), return the decoded object.  Optionally set the current decode
        cache [None].  If None, a new RollingCache is instantiated and used.
        You may also hit to the decoder that this node is to be treated as a
        map key [False].  This is used internally."""
        if not cache:
            cache = RollingCache()
        return self._decode(node, cache, as_map_key)

    def _decode(self, node, cache, as_map_key):
        tp = type(node)
        if tp is unicode:
            return self.decode_string(node, cache, as_map_key)
        elif tp is dict or tp is OrderedDict:
            return self.decode_hash(node, cache, as_map_key)
        elif tp is list:
            return self.decode_list(node, cache, as_map_key)
        elif tp is str:
            return self.decode_string(unicode(node, "utf-8"), cache, as_map_key)
        else:
            return node

    def decode_list(self, node, cache, as_map_key):
        """ Special case decodes map-as-array.
        Otherwise lists are treated as Python lists.

        Arguments follow the same convention as the top-level 'decode'
        function"""
        if node:
            decoded = self._decode(node[0], cache, as_map_key)
            if decoded == MAP_AS_ARR:
                return {self._decode(k, cache, True):
                        self._decode(v, cache, as_map_key)
                        for k,v in pairs(node[1:])}
            elif isinstance(decoded, Tag):
                return self.decode_tag(decoded.tag, self._decode(node[1], cache, as_map_key))
        return tuple(self._decode(x, cache, as_map_key) for x in node)

    def decode_string(self, string, cache, as_map_key):
        """ Decode a string - arguments follow the same convention as the
        top-level 'decode' function"""
        if is_cache_key(string):
            return self.parse_string(cache.decode(string, as_map_key), cache, as_map_key)
        if is_cacheable(string, as_map_key):
            cache.encode(string, as_map_key)
        return self.parse_string(string, cache, as_map_key)

    def decode_tag(self, tag, rep):
        decoder = self.decoders.get(tag, None)
        if decoder:
            return decoder.from_rep(rep)
        else:
            return self.options["default_decoder"].from_rep(tag, rep)

    def decode_hash(self, hash, cache, as_map_key):
        if len(hash) != 1:
            h = {}
            for k, v in hash.items():
                h[self._decode(k, cache, True)] = self._decode(v, cache, False)
            return transit_types.frozendict(h)
        else:
            key,value = hash.items()[0]
            key = self._decode(key, cache, True)
            if isinstance(key, Tag):
                return self.decode_tag(key.tag, self._decode(value, cache, as_map_key))
            else:
                return {key: self._decode(value, cache, False)}

    def parse_string(self, string, cache, as_map_key):
        if string.startswith(ESC):
            m = string[1]
            if m in self.decoders:
                return self.decoders[m].from_rep(string[2:])
            elif m == ESC or m == SUB or m == RES:
                return string[1:]
            elif m == "#":
                return Tag(string[2:])
            else:
                return self.options["default_decoder"].from_rep(string[1], string[2:])
        return string

    def register(self, key_or_tag, obj):
        """ Register a custom Transit tag and new parsing function with the
        decoder.  Also, you can optionally set the 'default_decoder' with
        this function.  Your new tag and parse/decode function will be added
        to the interal dictionary of decoders for this Decoder object"""
        if key_or_tag == "default_decoder":
            self.options["default_decoder"] = obj
        else:
            self.decoders[key_or_tag] = obj

