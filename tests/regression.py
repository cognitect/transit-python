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

# This test suite verifies that issues corrected remain corrected.
import unittest
import json

from transit.reader import Reader
from transit.writer import Writer
from transit.transit_types import Symbol, frozendict, true, false
from decimal import Decimal
from StringIO import StringIO

class RegressionBaseTest(unittest.TestCase):
    pass

def regression(name, value):
    class RegressionTest(RegressionBaseTest):

        def test_roundtrip(self):
            in_data = value
            io = StringIO()
            w = Writer(io, "json")
            w.write(in_data)
            r = Reader("json")
            out_data = r.read(StringIO(io.getvalue()))
            self.assertEqual(in_data, out_data)

    globals()["test_" + name + "_json"] = RegressionTest

regression("cache_consistency", ({"Problem?":true},
                                  Symbol("Here"),
                                  Symbol("Here")))
regression("one_pair_frozendict", frozendict({"a":1}))
regression("json_int_max", (2**53+100, 2**63+100))
regression("newline_in_string", "a\nb")
regression("big_decimal", Decimal("190234710272.2394720347203642836434"))

def int_boundary(value, rep_type):
    class JsonIntMaxTest(RegressionBaseTest):

        def test_max_is_number(self):
            for protocol in ("json", "json-verbose"):
                io = StringIO()
                w = Writer(io, protocol)
                w.write(value)
                marshaled = io.getvalue() #.decode('utf-8')
#                self.assertEqual([rep], marshaled)
                print marshaled
#                self.assertEqual(rep_type, type(json.loads(marshaled)[0]))

    globals()["test_json_int_boundary_" + str(value)] = JsonIntMaxTest

int_boundary(2**53-1, int)
int_boundary(2**53, unicode)
int_boundary(-2**53+1, int)
int_boundary(-2**53, unicode)

class BooleanTest(unittest.TestCase):
    """Even though we're roundtripping transit_types.true and
    transit_types.false now, make sure we can still write Python bools.

    Additionally, make sure we can still do basic logical evaluation on transit
    Boolean values.
    """
    def test_write_bool(self):
        for protocol in ("json", "json-verbose", "msgpack"):
            io = StringIO()
            w = Writer(io, protocol)
            w.write((True, False))
            r = Reader(protocol)
            io.seek(0)
            out_data = r.read(io)
            assert out_data[0] == true
            assert out_data[1] == false

    def test_basic_eval(self):
        assert true
        assert not false

    def test_or(self):
        assert true or false
        assert not (false or false)
        assert true or true

    def test_and(self):
        assert not (true and false)
        assert true and true
        assert not (false and false)

if __name__ == '__main__':
    unittest.main()
