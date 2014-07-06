## Copyright (c) Cognitect, Inc.
## All rights reserved.

import json
import msgpack
from decoder import Decoder
from collections import OrderedDict

class Reader(object):
    """ The top-level object for reading in Transit data and converting it to
    Python objects.  During initialization, you must specify the protocol used
    for unmarshalling the data- json or msgpack."""
    def __init__(self, protocol="json"):
        if protocol in ("json", "json_verbose"):
            self.reader = JsonUnmarshaler()
        else:
            self.reader = MsgPackUnmarshaler()

    def read(self, stream):
        """ Given a readable file descriptor object (something `load`able by
        msgpack or json), read the data, and return the Python representation
        of the contents."""
        return self.reader.load(stream)

    def register(self, key_or_tag, f_val):
        """ Register a custom transit tag and decoder/parser function for use
        during reads."""
        self.reader.decoder.register(key_or_tag, f_val)

class JsonUnmarshaler(object):
    """ The top-level Unmarshaler used by the Reader for JSON payloads.  While
    you may use this directly, it is strongly discouraged."""
    def __init__(self):
        self.decoder = Decoder()

    def load(self, stream):
        return self.decoder.decode(json.load(stream, object_pairs_hook=OrderedDict))


class MsgPackUnmarshaler(object):
    """ The top-level Unmarshaler used by the Reader for MsgPacke payloads.
    While you may use this directly, it is strongly discouraged."""
    def __init__(self):
        self.decoder = Decoder()

    def load(self, stream):
        return self.decoder.decode(msgpack.load(stream, object_pairs_hook=OrderedDict))

