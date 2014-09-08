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

from transit.reader import Reader
from transit.writer import Writer
from transit.transit_types import Symbol, frozendict
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

regression("cache_consistency", ({"Problem?":True},
                                  Symbol("Here"),
                                  Symbol("Here")))
regression("one_pair_frozendict", frozendict({"a":1}))
regression("json_int_max", (2**53+100, 2**63+100))
regression("newline_in_string", "a\nb")

if __name__ == '__main__':
    unittest.main()
