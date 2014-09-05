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

import json
import msgpack
from decoder import Decoder
from collections import OrderedDict

class Reader(object):
    """The top-level object for reading in Transit data and converting it to
    Python objects.  During initialization, you must specify the protocol used
    for unmarshalling the data- json or msgpack.
    """
    def __init__(self, protocol="json"):
        if protocol in ("json", "json_verbose"):
            self.reader = JsonUnmarshaler()
        else:
            self.reader = MsgPackUnmarshaler()
            self.unpacker = self.reader.unpacker

    def read(self, stream):
        """Given a readable file descriptor object (something `load`able by
        msgpack or json), read the data, and return the Python representation
        of the contents.
        """
        return self.reader.load(stream)

    def register(self, key_or_tag, f_val):
        """Register a custom transit tag and decoder/parser function for use
        during reads.
        """
        self.reader.decoder.register(key_or_tag, f_val)

    def readeach(self, stream):
        for o in self.reader.loadeach(stream):
            yield o

class JsonUnmarshaler(object):
    """The top-level Unmarshaler used by the Reader for JSON payloads.  While
    you may use this directly, it is strongly discouraged.
    """
    def __init__(self):
        self.decoder = Decoder()

    def load(self, stream):
        return self.decoder.decode(json.load(stream, object_pairs_hook=OrderedDict))

    def loadeach(self, stream):
        raise NotImplementedError

class MsgPackUnmarshaler(object):
    """The top-level Unmarshaler used by the Reader for MsgPacke payloads.
    While you may use this directly, it is strongly discouraged.
    """
    def __init__(self):
        self.decoder = Decoder()
        self.unpacker = msgpack.Unpacker(object_pairs_hook=OrderedDict)

    def load(self, stream):
        return self.decoder.decode(msgpack.load(stream, object_pairs_hook=OrderedDict))

    def loadeach(self, stream):
#        unpacker = msgpack.Unpacker(stream, object_pairs_hook=OrderedDict)
        for o in self.unpacker:
            yield self.decoder.decode(o)
