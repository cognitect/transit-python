# Copyright (c) Cognitect, Inc.
# All rights reserved.
import unittest
from transit.reader import JsonUnmarshaler, MsgPackUnmarshaler
from transit.writer import MsgPackMarshaler, JsonMarshaler
from transit.transit_types import Keyword, Symbol
from StringIO import StringIO

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
            marshaler = MsgPackMarshaler(io)
            marshaler.marshal_top(val)
            s = io.getvalue()
            io = StringIO(s)
            newval = MsgPackUnmarshaler().load(io)
            self.assertEqual(val, newval)

        def test_reencode_json(self):
            io = StringIO()
            marshaler = JsonMarshaler(io)
            marshaler.marshal_top(val)
            s = io.getvalue()
            print s
            io = StringIO(s)
            newval = JsonUnmarshaler().load(io)
            self.assertEqual(val, newval)

    globals()["test_" + name + "_json"] = ExemplarTest


exemplar("nil", None)
exemplar("true", True)
exemplar("false", False)
exemplar("zero", 0)
exemplar("one", 1)
exemplar("one_string", "hello")
exemplar("one_keyword", Keyword("hello"))

exemplar("ints", tuple(range(128)))

if __name__=='__main__':
    unittest.main()
