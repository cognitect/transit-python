## Copyright (c) Cognitect, Inc.
## All rights reserved.
import unittest
from transit.transit_types import Keyword

class KeyWordTest(unittest.TestCase):
    def test_equality(self):
        self.assertEqual(Keyword("foo"), Keyword("foo"))
        self.assertNotEqual(Keyword("foo"), Keyword("bar"))
        self.assertEqual(Keyword(u"foo"), Keyword("foo"))

        self.assertEqual((Keyword("foo"), Keyword("bar")), (Keyword("foo"), Keyword("bar")))