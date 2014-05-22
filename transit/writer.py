## Copyright (c) Cognitect, Inc.
## All rights reserved.

from constants import *
from rolling_cache import RollingCache
import msgpack
from handler import Handler
import re

def flatten_map(m):
    # This is the fastest way to do this in Python
    return [item for t in m.items() for item in t]

def re_fn(pat):
    compiled = re.compile(pat)
    def re_inner_fn(value):
        return compiled.match(value)

    return re_inner_fn

def is_unrecognized(s):
    s.startswith(RES +ESC)
is_escapable = re_fn("^" + re.escape(SUB) + "|" + ESC + "|" + RES)

def escape(s):
    if s.startswith(RES+ESC): # is_unrecognized
        return s[1:]
    elif is_escapable(s):
        return ESC+s
    else:
        return s

class Marshaler(object):
    def __init__(self, opts = {}):
        self.opts = opts
        self.handlers = Handler()

    def are_stringable_keys(self, m):
        for x in m.keys():
            if len(self.handlers[x].tag(x)) != 1:
                return False
        return True

    def emit_nil(self, _, as_map_key, cache):
        return self.emit_string(ESC, "_", None, True, cache) if as_map_key else self.emit_object(None)

    def emit_string(self, prefix, tag, string, as_map_key, cache):
        return self.emit_object(cache.encode(str(prefix) + tag + escape(string), as_map_key), as_map_key)

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

    def emit_map(self, m, _, cache):
        self.emit_map_start(len(m))
        for k, v in m.items():
            self.marshal(k, True, cache)
            self.marshal(v, False, cache)
        self.emit_map_end()

    def emit_cmap(self, m, _, cache):
        self.emit_map_start(1)
        self.emit_string(ESC, "#", "cmap", True, cache)
        self.marshal(flatten_map(m), False, cache)
        self.emit_map_end()

    def emit_tagged_map(self, tag, rep, _, cache):
        self.emit_map_start(1)
        self.emit_object(cache.encode(ESC + "#" + tag, True), True)
        self.marshal(rep, False, cache)
        self.emit_map_end()

    def emit_tagged_value(self, rep, as_map_key, cache):
        self.emit_map_start(1)
        self.emit_object(cache.encode(rep.keys()[0], True), True)
        self.marshal(rep.values()[0], False, cache)
        self.emit_map_end()

    def emit_encoded(self, tag, handler, obj, as_map_key, cache):
        rep = handler.rep(obj)
        if len(tag) == 1:
            if isinstance(rep, (str, unicode)):
                self.emit_string(ESC, tag, rep, as_map_key, cache)
            elif as_map_key or self.opts["prefer_strings"]:
                rep = handler.string_rep(obj)
                if isinstance(rep, (str, unicode)):
                    self.emit_string(ESC, tag, rep, as_map_key, cache)
                else:
                    raise AssertionError("Cannot be encoded as string: " + str({"tag": tag,
                                                                                "rep": rep,
                                                                                "obj": obj}))
            else:
                self.emit_tagged_map(tag, rep, False, cache)
        elif as_map_key:
            raise AssertionError("Cannot be used as a map key: " + str({"tag": tag,
                                                                                "rep": rep,
                                                                                "obj": obj}))
        else:
            self.emit_tagged_map(tag, rep, False, cache)



    def marshal(self, obj, as_map_key, cache):
        handler = self.handlers[obj]
        tag = handler.tag(obj)
        rep = handler.string_rep(obj) if as_map_key else handler.rep(obj)
        f = marshal_dispatch.get(tag)
        if f:
            f(self, rep, as_map_key, cache)
        else:
            self.emit_encoded(tag, handler, obj, as_map_key, cache)

    def marshal_top(self, obj, cache = None):
        if not cache:
            cache = RollingCache()

        handler = self.handlers[obj]

        tag = handler.tag(obj)
        if tag:
            if self.opts["quote_scalars"] and len(tag) == 1:
                self.marshal(Quote(), False, cache)
            else:
                self.marshal(obj, False, cache)
            self.flush()
        else:
            raise AssertionError("Handler must provide a non-nil tag: " + str(handler))


    def dispatch_map(self, rep, as_map_key, cache):
        if self.are_stringable_keys(rep):
            return self.emit_map(rep, as_map_key, cache)
        return self.emit_cmap(rep, as_map_key, cache)


marshal_dispatch = {"_": Marshaler.emit_nil,
                    "?": Marshaler.emit_boolean,
                    "s": lambda self, rep, as_map_key, cache: Marshaler.emit_string(self, "", "", rep, as_map_key, cache),
                    "i": Marshaler.emit_int,
                    "d": Marshaler.emit_double,
                    "'": Marshaler.emit_quoted,
                    "array": Marshaler.emit_array,
                    "map": Marshaler.dispatch_map,
                    "tagged_value": Marshaler.emit_tagged_value}


class MsgPackMarshaler(Marshaler):
    MSGPACK_MAX_INT = pow(2, 63)
    MSGPACK_MIN_INT = -pow(2, 63)

    default_opts = {"prefer_strings": False,
                    "max_int": MSGPACK_MAX_INT,
                    "min_int": MSGPACK_MIN_INT,
                    "quote_scalars": False}

    def __init__(self, io, opts={}):
        self.io = io
        self.packer = msgpack.Packer(autoreset=False)
        nopts = MsgPackMarshaler.default_opts.copy()
        nopts.update(opts)
        Marshaler.__init__(self, nopts)


    def emit_array_start(self, size):
        self.packer.pack_array_header(size)

    def emit_array_end(self):
        pass

    def emit_map_start(self, size):
        self.packer.pack_map_header(size)

    def emit_map_end(self):
        pass

    def emit_object(self, obj, as_map_key=False):
        self.packer.pack(obj)

    def flush(self):
        self.io.write(self.packer.bytes())
        self.io.flush()
        self.packer.reset()

REPLACE_RE = re.compile("\"")

class JsonMarshaler(Marshaler):
    JSON_MAX_INT = pow(2, 63)
    JSON_MIN_INT = -pow(2, 63)

    default_opts = {"prefer_strings": False,
                    "max_int": JSON_MAX_INT,
                    "min_int": JSON_MIN_INT,
                    "quote_scalars": False}

    ## Yes this is basically a custom JSON encoder,
    ## but I couldn't find an existing solution that worked
    ## well with the lazy writing method we have in this
    ## project.

    def __init__(self, io, opts={}):
        self.io = io
        nopts = JsonMarshaler.default_opts.copy()
        nopts.update(opts)
        self.started = [True]
        self.is_key = [None]
        Marshaler.__init__(self, nopts)

    def push_level(self):
        self.started.append(True)
        self.is_key.append(None)

    def pop_level(self):
        self.started.pop()
        self.is_key.pop()

    def push_map(self):
        self.started.append(True)
        self.is_key.append(True)

    def write_sep(self):
        if self.started[-1]:
            self.started[-1] = False
        else:
            if self.is_key[-1] is None:
                self.io.write(",")
            elif self.is_key[-1] is True:
                self.io.write(":")
                self.is_key[-1] = False
            else:
                self.io.write(",")
                self.is_key[-1] = True

    def emit_array_start(self, size):
        self.write_sep()
        self.io.write("[")
        self.push_level()


    def emit_array_end(self):
        self.pop_level()
        self.io.write("]")

    def emit_map_start(self, size):
        self.write_sep()
        self.io.write("{")
        self.push_map()

    def emit_map_end(self):
        self.pop_level()
        self.io.write("}")

    def emit_object(self, obj, as_map_key=False):
        tp = type(obj)
        self.write_sep()
        if tp == int or tp == long:
            self.io.write(str(obj))
        elif tp == float:
            self.io.write(str(obj))
        elif tp == bool:
            self.io.write("true" if obj else "false")
        elif obj == None:
            self.io.write("null")
        elif tp == str or tp == unicode:
            self.io.write("\"")
            self.io.write(obj.replace("\\", "\\\\").replace("\"", "\\\""))
            self.io.write("\"")
        else:
            raise AssertionError("Don't know how to encode: " + str(obj))

    def flush(self):
        self.io.flush()

