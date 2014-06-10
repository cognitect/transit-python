## Copyright (c) Cognitect, Inc.
## All rights reserved.

import yajl
import msgpack
from decoder import Decoder
from collections import OrderedDict
from rolling_cache import RollingCache

class State(object):
    def __init__(self, prev, cache):
        self.prev = prev
        self.cache = cache
    def push(self, state):
        return state(self, self.cache)
    def pop(self):
        return self.prev

class TopLevel(State):

    def __init__(self):
        State.__init__(self, None, RollingCache())
        self.val = None

    def handle(self, val):
        self.val = val
        self.cache = RollingCache()

class InMap(State):
    def __init__(self, prev, cache):
        State.__init__(self, prev, cache)
        self.map = {}
    def set_key(self, key):
        self.key = key
    def handle(self, val):
        self.map[self.key] = val

class InArray(State):
    def __init__(self, prev, cache):
        State.__init__(self, prev, cache)
        self.list = []
    def handle(self, val):
        self.list.append(val)

class ContentHandler(yajl.YajlContentHandler):

    def __init__(self, decoder):
        self.decoder = decoder
        self.state = TopLevel()

    def yajl_null(self, ctx):
        self.state.handle(None)

    def yajl_boolean(self, ctx, bool):
        self.state.handle(bool)

    def yajl_number(self, ctx, string):
        num = float(string) if '.' in string else int(string)
        self.state.handle(num)

    def yajl_string(self, ctx, string):
        string = unicode(string, 'utf-8')
        val = self.decoder.decode_string(string, self.state.cache, False)
        self.state.handle(val)

    def yajl_start_map(self, ctx):
        self.state = self.state.push(InMap)

    def yajl_map_key(self, ctx, string):
        val = self.decoder.decode_string(string, self.state.cache, True)
        self.state.set_key(val)

    def yajl_end_map(self, ctx):
        map = self.decoder.decode_map(self.state.map)
        self.state = self.state.pop()
        self.state.handle(map)

    def yajl_start_array(self, ctx):
        self.state = self.state.push(InArray)

    def yajl_end_array(self, ctx):
        list = tuple(self.state.list)
        self.state = self.state.pop()
        self.state.handle(list)

class JsonUnmarshaler(object):

    def __init__(self, decoder=None):
        self.decoder = decoder or Decoder()

    def load(self, stream):
        handler = ContentHandler(self.decoder)
        parser = yajl.YajlParser(handler)
        parser.allow_multiple_values = True
        parser.parse(f=stream)
        return handler.state.val

class MsgPackUnmarshaler(object):
    def __init__(self):
        self.decoder = Decoder()

    def load(self, stream):
        return self.decoder.decode(msgpack.load(stream, object_pairs_hook=OrderedDict))
