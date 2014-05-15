## Copyright (c) Cognitect, Inc.
## All rights reserved.

from constants import *



class Marshaler(object):
    def __init__(self, opts = {}):
        self.opts = opts

    def are_stringable_keys(self, m):
        for x in m.keys():
            if len(self.handlers[x].tag(x)) != 1:
                return False
        return True

    def emit_nil(self, _, as_map_key, cache):
        return self.emit_string(ESC, "_", None, True, cache) if as_map_key else self.emit_object(None)

    def emit_string(self, prefix, tag, string, as_map_key, cache):
        return self.emit_object(cache.encode("#" + str(prefix) + tag + escape(string), as_map_key), as_map_key)

    def emit_boolean(self, b, as_map_key, cache):
        return self.emit_string(ESC, "?", b, True, cache) if as_map_key else self.emit_object(b)


    def emit_quoted(self, o, as_map_key, cache):
        self.emit_map_start(1)
        self.emit_string(TAG, "'", None, True, cache)
        self.marshal(o, False, cache)
        self.emit_map_end()

    def emit_int(self, i, as_map_key, cache):
        if as_map_key or i > self.opts["max_int"] or i < self.opts["min_int"]:
            return self.emit_string(ESC, "i", str(i), as_map_key, cache)
        else:
            return self.emit_object(i, as_map_key)

    def emit_double(self, d, as_map_key, cache):
        return self.emit_string(ESC, "d", d, True, cache) if as_map_key else self.emit_object(d)

    def emit_array(self, a, _, cache):
        self.emit_array_start(len(a))
        map(lambda x: self.marshal(x, False, cache), a)
        self.emit_array_end()




