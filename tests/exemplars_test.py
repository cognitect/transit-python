# -*- coding: utf-8 -*-
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
import unittest

# then import transit stuff
from transit.reader import Reader, JsonUnmarshaler, MsgPackUnmarshaler
from transit.writer import Writer
from transit.transit_types import Keyword, Symbol, URI, frozendict, TaggedValue, Link, true, false
from StringIO import StringIO
from transit.helpers import mapcat
from helpers import ints_centered_on, hash_of_size, array_of_symbools
from uuid import UUID
from datetime import datetime
import dateutil.tz
from math import isnan

class ExemplarBaseTest(unittest.TestCase):
    pass

def exemplar(name, val):
    class ExemplarTest(ExemplarBaseTest):

        def test_json(self):
            with open("../transit-format/examples/0.8/simple/" + name + ".json", 'r') as stream:
                data = Reader(protocol="json").read(stream)
                self.assertEqual(val, data)

        def test_msgpack(self):
            with open("../transit-format/examples/0.8/simple/" + name + ".mp", 'r') as stream:
                data = Reader(protocol="msgpack").read(stream)
                self.assertEqual(val, data)

        def test_json_verbose(self):
            with open("../transit-format/examples/0.8/simple/" + name + ".verbose.json", 'r') as stream:
                data = Reader(protocol="json_verbose").read(stream)
                self.assertEqual(val, data)

        def test_reencode_msgpack(self):
            io = StringIO()
            writer = Writer(io, protocol="msgpack")
            writer.write(val)
            s = io.getvalue()
            io = StringIO(s)

            reader = Reader(protocol="msgpack")
            newval = reader.read(io)
            self.assertEqual(val, newval)

        def test_reencode_json(self):
            io = StringIO()
            writer = Writer(io, protocol="json")
            writer.write(val)
            s = io.getvalue()
            # Uncomment when debugging to see what payloads fail
            # print(s)
            io = StringIO(s)
            reader = Reader(protocol="json")
            newval = reader.read(io)
            self.assertEqual(val, newval)

        # test json verbose
        def test_reencode_json_verbose(self):
            io = StringIO()
            writer = Writer(io, protocol="json_verbose")
            writer.write(val)
            s = io.getvalue()
            io = StringIO(s)
            reader = Reader(protocol="json_verbose")
            newval = reader.read(io)
            self.assertEqual(val, newval)

        def assertEqual(self, val, data):
            try:
                return unittest.TestCase.assertEqual(self, val, data)
            except AssertionError as e:
                if not False in [isnan(v) and isnan(d) or isnan(v) == isnan(d)
                                 for v, d in zip (val, data)]:
                    return unittest.TestCase.assertEqual(self, filter(lambda x: not isnan(x), val),
                                                               filter(lambda x: not isnan(x), data))
                else:
                    e.args += (name, "failed")
                    raise

    globals()["test_" + name + "_json"] = ExemplarTest

ARRAY_SIMPLE = (1, 2, 3)
ARRAY_MIXED = (0, 1, 2.0, true, false, 'five', Keyword("six"), Symbol("seven"), '~eight', None)
ARRAY_NESTED = (ARRAY_SIMPLE, ARRAY_MIXED)
SMALL_STRINGS = ("", "a", "ab", "abc", "abcd", "abcde", "abcdef")
POWERS_OF_TWO = tuple(map(lambda x: pow(2, x), range(66)))
INTERESTING_INTS = tuple(mapcat(lambda x: ints_centered_on(x, 2), POWERS_OF_TWO))

SYM_STRS = ["a", "ab", "abc", "abcd", "abcde", "a1", "b2", "c3", "a_b"]
SYMBOLS = tuple(map(Symbol, SYM_STRS))
KEYWORDS = tuple(map(Keyword, SYM_STRS))


UUIDS = (UUID('5a2cbea3-e8c6-428b-b525-21239370dd55'),
         UUID('d1dc64fa-da79-444b-9fa4-d4412f427289'),
         UUID('501a978e-3a3e-4060-b3be-1cf2bd4b1a38'),
         UUID('b3ba141a-a776-48e4-9fae-a28ea8571f58'))

URIS = (
  URI(u'http://example.com'),
  URI(u'ftp://example.com'),
  URI(u'file:///path/to/file.txt'),
  URI(u'http://www.詹姆斯.com/'))

DATES = tuple(map(lambda x: datetime.fromtimestamp(x/1000.0, tz=dateutil.tz.tzutc()),
                  [-6106017600000, 0, 946728000000, 1396909037000]))

SET_SIMPLE = frozenset(ARRAY_SIMPLE)
SET_MIXED = frozenset(ARRAY_MIXED)
SET_NESTED = frozenset([SET_SIMPLE, SET_MIXED])

MAP_SIMPLE = frozendict({Keyword("a"): 1,
                         Keyword("b"): 2,
                         Keyword("c"): 3})

MAP_MIXED = frozendict({Keyword("a"): 1,
                        Keyword("b"): u"a string",
                        Keyword("c"): true})

MAP_NESTED = frozendict({Keyword("simple"): MAP_SIMPLE,
                         Keyword("mixed"): MAP_MIXED})

exemplar("nil", None)
exemplar("true", true)
exemplar("false", false)
exemplar("zero", 0)
exemplar("one", 1)
exemplar("one_string", "hello")
exemplar("one_keyword", Keyword("hello"))
exemplar("one_symbol", Symbol("hello"))
exemplar("one_date", datetime.fromtimestamp(946728000000/1000.0, dateutil.tz.tzutc()))
exemplar("vector_simple", ARRAY_SIMPLE)
exemplar("vector_empty", ())
exemplar("vector_mixed", ARRAY_MIXED)
exemplar("vector_nested", ARRAY_NESTED)
exemplar("small_strings", SMALL_STRINGS)
exemplar("strings_tilde", tuple(map(lambda x: "~" + x, SMALL_STRINGS)))
exemplar("strings_hash", tuple(map(lambda x: "#" + x, SMALL_STRINGS)))
exemplar("strings_hat", tuple(map(lambda x: "^" + x, SMALL_STRINGS)))
exemplar("ints", tuple(range(128)))
exemplar("small_ints", ints_centered_on(0))
exemplar("ints_interesting", INTERESTING_INTS)
exemplar("ints_interesting_neg", tuple(map(lambda x: -x, INTERESTING_INTS)))
exemplar("doubles_small", tuple(map(float, ints_centered_on(0))))
exemplar("doubles_interesting", (-3.14159, 3.14159, 4E11, 2.998E8, 6.626E-34))
exemplar("one_uuid", UUIDS[0])
exemplar("uuids", UUIDS)
exemplar("one_uri", URIS[0])
exemplar("uris", URIS)
exemplar("dates_interesting", DATES)
exemplar("symbols", SYMBOLS)
exemplar("keywords", KEYWORDS)
exemplar("list_simple", ARRAY_SIMPLE)
exemplar("list_empty", ())
exemplar("list_mixed", ARRAY_MIXED)
exemplar("list_nested", ARRAY_NESTED)
exemplar("set_simple", SET_SIMPLE)
exemplar("set_empty", set())
exemplar("set_mixed", SET_MIXED)
exemplar("set_nested", SET_NESTED)
exemplar("map_simple", MAP_SIMPLE)
exemplar("map_mixed", MAP_MIXED)
exemplar("map_nested", MAP_NESTED)
exemplar("map_string_keys", {"first": 1, "second": 2, "third": 3})
exemplar("map_numeric_keys", {1: "one", 2: "two"})
exemplar("map_vector_keys", frozendict([[(1, 1), "one"],
                                        [(2, 2), "two"]]))


exemplar("map_unrecognized_vals", {Keyword("key"): "~Unrecognized"})
#exemplar("map_unrecognized_keys", )
exemplar("vector_unrecognized_vals", ("~Unrecognized",))
exemplar("vector_1935_keywords_repeated_twice", tuple(array_of_symbools(1935, 1935*2)))
exemplar("vector_1936_keywords_repeated_twice", tuple(array_of_symbools(1936, 1936*2)))
exemplar("vector_1937_keywords_repeated_twice", tuple(array_of_symbools(1937, 1937*2)))

exemplar("map_10_items", hash_of_size(10))
exemplar("maps_two_char_sym_keys", ({Symbol("aa"): 1, Symbol("bb"): 2},
                                    {Symbol("aa"): 3, Symbol("bb"): 4},
                                    {Symbol("aa"): 5, Symbol("bb"): 6}))

exemplar("maps_three_char_sym_keys", ({Symbol("aaa"): 1, Symbol("bbb"): 2},
                                      {Symbol("aaa"): 3, Symbol("bbb"): 4},
                                      {Symbol("aaa"): 5, Symbol("bbb"): 6}))

exemplar("maps_four_char_sym_keys", ({Symbol("aaaa"): 1, Symbol("bbbb"): 2},
                                     {Symbol("aaaa"): 3, Symbol("bbbb"): 4},
                                     {Symbol("aaaa"): 5, Symbol("bbbb"): 6}))

exemplar("maps_two_char_string_keys", ({"aa": 1, "bb": 2},
                                       {"aa": 3, "bb": 4},
                                       {"aa": 5, "bb": 6}))

exemplar("maps_three_char_string_keys", ({"aaa": 1, "bbb": 2},
                                         {"aaa": 3, "bbb": 4},
                                         {"aaa": 5, "bbb": 6}))

exemplar("maps_four_char_string_keys", ({"aaaa": 1, "bbbb": 2},
                                        {"aaaa": 3, "bbbb": 4},
                                        {"aaaa": 5, "bbbb": 6}))

exemplar("maps_unrecognized_keys", (TaggedValue("abcde", Keyword("anything")),
                                   TaggedValue("fghij", Keyword("anything-else")),))

exemplar("vector_special_numbers", (float("nan"), float("inf"), float("-inf")))

# Doesn't exist in simple examples but gave me tests to verify Link.
#exemplar("link", Link("http://www.blah.com", "test", "test", "link", "test"))

def make_hash_exemplar(n):
    exemplar("map_%s_nested" % (n,), {Keyword("f"): hash_of_size(n),
                                      Keyword("s"): hash_of_size(n)})
map(make_hash_exemplar, [10, 1935, 1936, 1937])

if __name__=='__main__':
    unittest.main()
    #import cProfile
    #import pstats
    #cProfile.run('unittest.main()', 'exemptests')
    #p = pstats.Stats('exemptests')
    #p.sort_stats('time')
    #p.print_stats()

