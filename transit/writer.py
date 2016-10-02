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

import sys
import msgpack
import re
from transit import pyversion
from transit.constants import SUB, ESC, RES, MAP_AS_ARR, QUOTE
from transit.rolling_cache import RollingCache
from transit.write_handlers import WriteHandler
from transit.transit_types import TaggedValue

ESCAPE_DCT = {
    '\\': u'\\\\',
    '"': u'\\"',
    '\b': u'\\b',
    '\f': u'\\f',
    '\n': u'\\n',
    '\r': u'\\r',
    '\t': u'\\t',
}
for i in range(0x20):
  ESCAPE_DCT.setdefault(chr(i), '\\u{0:04x}'.format(i))



class Writer(object):
    """The top-level object for writing out Python objects and converting them
    to Transit data.  During initialization, you must specify the protocol used
    for marshalling the data- json or msgpack.  You must also specify the io
    source used for writing (a file descriptor).  You may optionally pass in
    an options dictionary that will be forwarded onto the Marshaler.
    The cache is enabled by default.
    """
    def __init__(self, io, protocol="json", opts={"cache_enabled": True}):
        if protocol == "json":
            self.marshaler = JsonMarshaler(io, opts=opts)
        elif protocol == "json_verbose":
            self.marshaler = VerboseJsonMarshaler(io, opts=opts)
        elif protocol == "msgpack":
            self.marshaler = MsgPackMarshaler(io, opts=opts)
        else:
            raise ValueError("'" + protocol + "' is not a supported protocol. " +
                             "Protocol must be 'json', 'json_verbose', or 'msgpack'.")

    def write(self, obj):
        """Given a Python object, marshal it into Transit data and write it to
        the 'io' source.
        """
        self.marshaler.marshal_top(obj)

    def register(self, obj_type, handler_class):
        """Register custom converters for object types present in your
        application.  This allows you to extend Transit to encode new types.
        You must specify the obj type to be encoded, and the handler class
        that should be used by the Marshaler during write-time.
        """
        self.marshaler.register(obj_type, handler_class)


def flatten_map(m):
    """Expand a dictionary's items into a flat list
    """
    # This is the fastest way to do this in Python
    return [item for t in m.items() for item in t]


def re_fn(pat):
    compiled = re.compile(pat)
    def re_inner_fn(value):
        return compiled.match(value)

    return re_inner_fn

is_escapable = re_fn("^" + re.escape(SUB) + "|" + ESC + "|" + RES)


def escape(s):
    if s is MAP_AS_ARR:
        return MAP_AS_ARR
    if is_escapable(s):
        return ESC+s
    else:
        return s


class Marshaler(object):
    """The base Marshaler from which all Marshalers inherit.

    The Marshaler specifies how to emit Transit data given encodeable Python
    objects.  The end of this process is specialized by other Marshalers to
    covert the final result into an on-the-wire payload (JSON or MsgPack).
    """
    def __init__(self, opts={}):
        self.opts = opts
        self._init_handlers()

    def _init_handlers(self):
        self.handlers = WriteHandler()

    def are_stringable_keys(self, m):
        """Test whether the keys within a map are stringable - a simple map,
        that can be optimized and whose keys can be cached
        """
        for x in m.keys():
            if len(self.handlers[x].tag(x)) != 1:
                return False
        return True

    def emit_nil(self, _, as_map_key, cache):
        return self.emit_string(ESC, "_", None, True, cache) if as_map_key else self.emit_object(None)

    def emit_string(self, prefix, tag, string, as_map_key, cache):
        encoded = cache.encode(str(prefix)+tag+string, as_map_key)
        # TODO: Remove this optimization for the time being - it breaks cache
        #if "cache_enabled" in self.opts and is_cacheable(encoded, as_map_key):
        #    return self.emit_object(cache.value_to_key[encoded], as_map_key)
        return self.emit_object(encoded, as_map_key)

    def emit_boolean(self, b, as_map_key, cache):
        return self.emit_string(ESC, "?", b, True, cache) if as_map_key else self.emit_object(b)

    def emit_int(self, tag, i, rep, as_map_key, cache):
        if isinstance(rep, int):
          if i <= self.opts["max_int"] and i >= self.opts["min_int"]:
            return self.emit_object(i, as_map_key)
          else:
            return self.emit_string(ESC, tag, str(rep), as_map_key, cache)
        else:
            return self.emit_string(ESC, tag, rep, as_map_key, cache)

    def emit_double(self, d, as_map_key, cache):
        return self.emit_string(ESC, "d", d, True, cache) if as_map_key else self.emit_object(d)

    def emit_array(self, a, _, cache):
        self.emit_array_start(len(a))
        for x in a:
            self.marshal(x, False, cache)
        self.emit_array_end()

    def emit_map(self, m, _, cache):# use map as object from above, have to overwrite default parser.
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

    def emit_tagged(self, tag, rep, cache):
        self.emit_array_start(2)
        self.emit_string(ESC, "#", tag, False, cache)
        self.marshal(rep, False, cache)
        self.emit_array_end()

    def emit_encoded(self, tag, handler, obj, as_map_key, cache):
        rep = handler.rep(obj)
        if len(tag) == 1:
            if pyversion.isstring(rep):
                self.emit_string(ESC, tag, rep, as_map_key, cache)
            elif as_map_key or self.opts["prefer_strings"]:
                rep = handler.string_rep(obj)
                if pyversion.isstring(rep):
                    self.emit_string(ESC, tag, rep, as_map_key, cache)
                else:
                    raise AssertionError("Cannot be encoded as string: " + str({"tag": tag,
                                                                                "rep": rep,
                                                                                "obj": obj}))
            else:
                self.emit_tagged(tag, rep, cache)
        elif as_map_key:
            raise AssertionError("Cannot be used as a map key: " + str({"tag": tag,
                                                                        "rep": rep,
                                                                        "obj": obj}))
        else:
            self.emit_tagged(tag, rep, cache)

    def marshal(self, obj, as_map_key, cache):
        """Marshal an individual obj, potentially as part of another container
        object (like a list/dictionary/etc).  Specify if this object is a key
        to a map/dict, and pass in the current cache being used.
        This method should only be called by a top-level marshalling call
        and should not be considered an entry-point for integration.
        """
        handler = self.handlers[obj]
        tag = handler.tag(obj)
        f = marshal_dispatch.get(tag)

        if f:
            f(self, obj, handler.string_rep(obj) if as_map_key else handler.rep(obj), as_map_key, cache)
        else:
            self.emit_encoded(tag, handler, obj, as_map_key, cache)

    def marshal_top(self, obj, cache=None):
        """Given a complete object that needs to be marshaled into Transit
        data, and optionally a cache, dispatch accordingly, and flush the data
        directly into the IO stream.
        """
        if not cache:
            cache = RollingCache()

        handler = self.handlers[obj]

        tag = handler.tag(obj)
        if tag:
            if len(tag) == 1:
                self.marshal(TaggedValue(QUOTE, obj), False, cache)
            else:
                self.marshal(obj, False, cache)
            self.flush()
        else:
            raise AssertionError("Handler must provide a non-nil tag: " + str(handler))

    def dispatch_map(self, rep, as_map_key, cache):
        """Used to determine and dipatch the writing of a map - a simple
        map with strings as keys, or a complex map, whose keys are also
        compound types.
        """
        if self.are_stringable_keys(rep):
            return self.emit_map(rep, as_map_key, cache)
        return self.emit_cmap(rep, as_map_key, cache)

    def register(self, obj_type, handler_class):
        """Register custom converters for object types present in your
        application.  This allows you to extend Transit to encode new types.
        You must specify the obj type to be encoded, and the handler class
        that should be used by this marshaller.
        """
        self.handlers[obj_type] = handler_class

marshal_dispatch = {"_": lambda self, obj, rep, as_map_key, cache: self.emit_nil(rep, as_map_key, cache),
                    "?": lambda self, obj, rep, as_map_key, cache: self.emit_boolean(rep, as_map_key, cache),
                    "s": lambda self, obj, rep, as_map_key, cache: self.emit_string("", "", escape(rep), as_map_key, cache),
                    "i": lambda self, i, rep, as_map_key, cache: self.emit_int("i", i, rep, as_map_key, cache),
                    "n": lambda self, i, rep, as_map_key, cache: self.emit_int("n", i, rep, as_map_key, cache),
                    "d": lambda self, obj, rep, as_map_key, cache: self.emit_double(rep, as_map_key, cache),
                    "'": lambda self, obj, rep, _, cache: self.emit_tagged("'", rep, cache),
                    "array": lambda self, obj, rep, as_map_key, cache: self.emit_array(rep, as_map_key, cache),
                    "map": lambda self, obj, rep, as_map_key, cache: self.dispatch_map(rep, as_map_key, cache)}


class MsgPackMarshaler(Marshaler):
    """The Marshaler tailor to MsgPack.  To use this Marshaler, specify the
    'msgpack' protocol when creating a Writer.
    """
    MSGPACK_MAX_INT = pow(2, 63) - 1
    MSGPACK_MIN_INT = -pow(2, 63)

    default_opts = {"prefer_strings": False,
                    "max_int": MSGPACK_MAX_INT,
                    "min_int": MSGPACK_MIN_INT}

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
    """The Marshaler tailor to JSON.  To use this Marshaler, specify the
    'json' protocol when creating a Writer.
    """
    JSON_MAX_INT = pow(2, 53) - 1
    JSON_MIN_INT = -pow(2, 53) + 1

    default_opts = {"prefer_strings": True,
                    "max_int": JSON_MAX_INT,
                    "min_int": JSON_MIN_INT}

    def __init__(self, io, opts={}):
        self.io = io
        nopts = JsonMarshaler.default_opts.copy()
        nopts.update(opts)
        self.started = [True]
        self.is_key = [None]
        Marshaler.__init__(self, nopts)
        self.flush = self.io.flush

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
            last = self.is_key[-1]
            if last:
                self.io.write(u":")
                self.is_key[-1] = False
            elif last is False:
                self.io.write(u",")
                self.is_key[-1] = True
            else:
                self.io.write(u",")

    def emit_array_start(self, size):
        self.write_sep()
        self.io.write(u"[")
        self.push_level()

    def emit_array_end(self):
        self.pop_level()
        self.io.write(u"]")

    def emit_map(self, m, _, cache):
        """Emits array as per default JSON spec."""
        self.emit_array_start(None)
        self.marshal(MAP_AS_ARR, False, cache)
        for k, v in m.items():
            self.marshal(k, True, cache)
            self.marshal(v, False, cache)
        self.emit_array_end()

    def emit_map_start(self, size):
        self.write_sep()
        self.io.write(u"{")
        self.push_map()

    def emit_map_end(self):
        self.pop_level()
        self.io.write(u"}")

    def emit_object(self, obj, as_map_key=False):
        tp = type(obj)
        self.write_sep()
        if tp in pyversion.string_types:
            self.io.write(u"\"")
            self.io.write(u"".join([(ESCAPE_DCT[c]) if c in ESCAPE_DCT else c for c in obj]))
            self.io.write(u"\"")
        elif pyversion.isnumber_type(tp):
            self.io.write(pyversion.unicode_type(obj))
        elif tp is bool:
            self.io.write(u"true" if obj else u"false")
        elif obj is None:
            self.io.write(u"null")
        else:
          raise AssertionError("Don't know how to encode: " + str(obj) + " of type: " + str(type(obj)))


class VerboseSettings(object):
    """Mixin for JsonMarshaler that adds support for Verbose output/input.
    Verbosity is only suggest for debuging/inspecting purposes.
    """
    @staticmethod
    def _verbose_handlers(handlers):
        for k, v in pyversion.iteritems(handlers):
            if hasattr(v, "verbose_handler"):
                handlers[k] = v.verbose_handler()
        return handlers

    def _init_handlers(self):
        self.handlers = self._verbose_handlers(WriteHandler())

    def emit_string(self, prefix, tag, string, as_map_key, cache):
        return self.emit_object(pyversion.unicode_type(prefix) + tag + string, as_map_key)

    def emit_map(self, m, _, cache):
        self.emit_map_start(len(m))
        for k, v in m.items():
            self.marshal(k, True, cache)
            self.marshal(v, False, cache)
        self.emit_map_end()

    def emit_tagged(self, tag, rep, cache):
        self.emit_map_start(1)
        self.emit_object(ESC + "#" + tag, True)
        self.marshal(rep, False, cache)
        self.emit_map_end()


class VerboseJsonMarshaler(VerboseSettings, JsonMarshaler):
    """JsonMarshaler class with VerboseSettings mixin."""
    pass  # all from inheritance and mixin
