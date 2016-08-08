# Copyright 2014 Cognitect. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from transit import transit_types
from transit.constants import MAP_AS_ARR, ESC, SUB, RES
from collections import OrderedDict
from transit.helpers import pairs
import transit.read_handlers as rh
from transit.rolling_cache import RollingCache, is_cacheable, is_cache_key
from transit.transit_types import true, false
import six


class Tag(object):
    def __init__(self, tag):
        self.tag = tag

default_options = {"decoders": {"_": rh.NoneHandler,
                                ":": rh.KeywordHandler,
                                "$": rh.SymbolHandler,
                                "?": rh.BooleanHandler,
                                "i": rh.IntHandler,
                                "d": rh.FloatHandler,
                                "f": rh.BigDecimalHandler,
                                "u": rh.UuidHandler,
                                "r": rh.UriHandler,
                                "t": rh.DateHandler,
                                "m": rh.DateHandler,
                                "n": rh.BigIntegerHandler,
                                "z": rh.SpecialNumbersHandler,
                                "link": rh.LinkHandler,
                                "list": rh.ListHandler,
                                "set": rh.SetHandler,
                                "cmap": rh.CmapHandler,
                                "'": rh.IdentityHandler},
                   "default_decoder": rh.DefaultHandler}

ground_decoders = {"_": rh.NoneHandler,
                   "?": rh.BooleanHandler,
                   "i": rh.IntHandler,
                   "'": rh.IdentityHandler}


class Decoder(object):
    """The Decoder is the lowest level entry point for parsing, decoding, and
    fully converting Transit data into Python objects.

    During the creation of a Decoder object, you can specify custom options
    in a dictionary.  One such option is 'decoders'.  Note that while you
    can specify your own decoders and override many of the built in decoders,
    some decoders are silently enforced and cannot be overriden.  These are
    known as Ground Decoders, and are needed to maintain bottom-tier
    compatibility.
    """
    def __init__(self, options={}):
        self.options = default_options.copy()
        self.options.update(options)

        self.decoders = self.options["decoders"]
        # Always ensure we control the ground decoders
        self.decoders.update(ground_decoders)

    def decode(self, node, cache=None, as_map_key=False):
        """Given a node of data (any supported decodeable obj - string, dict,
        list), return the decoded object.  Optionally set the current decode
        cache [None].  If None, a new RollingCache is instantiated and used.
        You may also hit to the decoder that this node is to be treated as a
        map key [False].  This is used internally.
        """
        if not cache:
            cache = RollingCache()
        return self._decode(node, cache, as_map_key)

    def _decode(self, node, cache, as_map_key):
        tp = type(node)
        # handles py3 strings(unicode) and py2 unicode
        if isinstance(node, six.text_type):
            return self.decode_string(node, cache, as_map_key)
        if tp is dict or tp is OrderedDict:
            return self.decode_hash(node, cache, as_map_key)
        if tp is list:
            return self.decode_list(node, cache, as_map_key)
        if tp is bool:
            return true if node else false
        # handles py2 strings, py3 strings handled above
        if isinstance(node, six.string_types):
            return self.decode_string(six.text_type(node), cache, as_map_key)
        return node

    def decode_list(self, node, cache, as_map_key):
        """Special case decodes map-as-array.
        Otherwise lists are treated as Python lists.

        Arguments follow the same convention as the top-level 'decode'
        function.
        """
        if node:
            if node[0] == MAP_AS_ARR:
                # key must be decoded before value for caching to work.
                returned_dict = {}
                for k, v in pairs(node[1:]):
                    key = self._decode(k, cache, True)
                    val = self._decode(v, cache, as_map_key)
                    returned_dict[key] = val
                return transit_types.frozendict(returned_dict)

            decoded = self._decode(node[0], cache, as_map_key)
            if isinstance(decoded, Tag):
                return self.decode_tag(decoded.tag,
                                       self._decode(node[1], cache, as_map_key))
        return tuple(self._decode(x, cache, as_map_key) for x in node)

    def decode_string(self, string, cache, as_map_key):
        """Decode a string - arguments follow the same convention as the
        top-level 'decode' function.
        """
        if is_cache_key(string):
            return self.parse_string(cache.decode(string, as_map_key),
                                     cache, as_map_key)
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
                # crude/verbose implementation, but this is only version that
                # plays nice w/cache for both msgpack and json thus far.
                # -- e.g., we have to specify encode/decode order for key/val
                # -- explicitly, all implicit ordering has broken in corner
                # -- cases, thus these extraneous seeming assignments
                key = self._decode(k, cache, True)
                val = self._decode(v, cache, False)
                h[key] = val
            return transit_types.frozendict(h)
        else:
            keyv = list(hash)[0]
            value = hash[keyv]
            key = self._decode(keyv, cache, True)
            if isinstance(key, Tag):
                return self.decode_tag(
                    key.tag,
                    self._decode(value, cache, as_map_key))
        return transit_types.frozendict(
            {key: self._decode(value, cache, False)})

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
                return self.options["default_decoder"].from_rep(string[1],
                                                                string[2:])
        return string

    def register(self, key_or_tag, obj):
        """Register a custom Transit tag and new parsing function with the
        decoder.  Also, you can optionally set the 'default_decoder' with
        this function.  Your new tag and parse/decode function will be added
        to the interal dictionary of decoders for this Decoder object.
        """
        if key_or_tag == "default_decoder":
            self.options["default_decoder"] = obj
        else:
            self.decoders[key_or_tag] = obj
