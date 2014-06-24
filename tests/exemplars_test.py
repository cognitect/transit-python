# -*- coding: utf-8 -*-
# Copyright (c) Cognitect, Inc.
# All rights reserved.
import unittest

# get parent directory into python path
import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + os.path.sep + os.path.pardir))

# then import transit stuff
from transit.reader import JsonUnmarshaler, MsgPackUnmarshaler
from transit.writer import Writer
from transit.transit_types import Keyword, Symbol, URI, frozendict, TaggedValue
from StringIO import StringIO
from transit.helpers import mapcat
from helpers import ints_centered_on, hash_of_size, array_of_symbools
from uuid import UUID
from datetime import datetime
import dateutil.tz

class ExemplarBaseTest(unittest.TestCase):
    pass

def exemplar(name, val):
    class ExemplarTest(ExemplarBaseTest):
        def test_json(self):
            with open("../transit/simple-examples/" + name + ".json", 'r') as stream:
                data = JsonUnmarshaler().load(stream)
                self.assertEqual(val, data)

        def test_msgpack(self):
            with open("../transit/simple-examples/" + name + ".mp", 'r') as stream:
                data = MsgPackUnmarshaler().load(stream)
                self.assertEqual(val, data)

        def test_reencode_msgpack(self):
            io = StringIO()
            marshaler = Writer(io, protocol="msgpack")
            marshaler.marshal_top(val)
            s = io.getvalue()
            io = StringIO(s)
            newval = MsgPackUnmarshaler().load(io)
            self.assertEqual(val, newval)

        def test_reencode_json(self):
            io = StringIO()
            marshaler = Writer(io, protocol="json")
            marshaler.marshal_top(val)
            s = io.getvalue()
            # Uncomment when debugging to see what payloads fail
            # print(s)
            io = StringIO(s)
            newval = JsonUnmarshaler().load(io)
            self.assertEqual(val, newval)

        # test json verbose
#        def test_reencode_json_verbose(self):
#            io = StringIO()
#            marshaler = Writer(io, protocol="json_verbose")
#            self.assertEqual(True, True)

    globals()["test_" + name + "_json"] = ExemplarTest

ARRAY_SIMPLE = (1, 2, 3)
ARRAY_MIXED = (0, 1, 2.0, True, False, 'five', Keyword("six"), Symbol("seven"), '~eight', None)
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
                        Keyword("c"): True})

MAP_NESTED = frozendict({Keyword("simple"): MAP_SIMPLE,
                         Keyword("mixed"): MAP_MIXED})

exemplar("nil", None)
exemplar("true", True)
exemplar("false", False)
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


exemplar("map_unrecognized_vals", {Keyword("key"): "`~notrecognized"})
#exemplar("map_unrecognized_keys", )
exemplar("vector_unrecognized_vals", ("`~notrecognized",))
exemplar("vector_93_keywords_repeated_twice", tuple(array_of_symbools(93, 186)))
exemplar("vector_94_keywords_repeated_twice", tuple(array_of_symbools(94, 188)))
exemplar("vector_95_keywords_repeated_twice", tuple(array_of_symbools(95, 190)))

exemplar("map_10_items", hash_of_size(10))
exemplar("maps_two_char_sym_keys", ({Keyword("aa"): 1, Keyword("bb"): 2},
                                    {Keyword("aa"): 3, Keyword("bb"): 4},
                                    {Keyword("aa"): 5, Keyword("bb"): 6}))

exemplar("maps_three_char_sym_keys", ({Keyword("aaa"): 1, Keyword("bbb"): 2},
                                      {Keyword("aaa"): 3, Keyword("bbb"): 4},
                                      {Keyword("aaa"): 5, Keyword("bbb"): 6}))

exemplar("maps_four_char_sym_keys", ({Keyword("aaaa"): 1, Keyword("bbbb"): 2},
                                     {Keyword("aaaa"): 3, Keyword("bbbb"): 4},
                                     {Keyword("aaaa"): 5, Keyword("bbbb"): 6}))

exemplar("maps_two_char_string_keys", ({"aa": 1, "bb": 2},
                                       {"aa": 3, "bb": 4},
                                       {"aa": 5, "bb": 6}))

exemplar("maps_three_char_string_keys", ({"aaa": 1, "bbb": 2},
                                         {"aaa": 3, "bbb": 4},
                                         {"aaa": 5, "bbb": 6}))

exemplar("maps_four_char_string_keys", ({"aaaa": 1, "bbbb": 2},
                                        {"aaaa": 3, "bbbb": 4},
                                        {"aaaa": 5, "bbbb": 6}))

exemplar("maps_unrecognized_keys", (TaggedValue("~#abcde", Keyword("anything")),
                                   TaggedValue("~#fghij", Keyword("anything-else")),))

def make_hash_exemplar(n):
    exemplar("map_%s_nested" % (n,), {Keyword("f"): hash_of_size(n),
                                      Keyword("s"): hash_of_size(n)})
map(make_hash_exemplar, [10, 90, 91, 92, 93, 94, 95])

if __name__=='__main__':
    unittest.main()
    #import cProfile
    #import pstats
    #cProfile.run('unittest.main()', 'exemptests')
    #p = pstats.Stats('exemptests')
    #p.sort_stats('time')
    #p.print_stats()

