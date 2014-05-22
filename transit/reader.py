## Copyright (c) Cognitect, Inc.
## All rights reserved.

import json
import msgpack
from decoder import Decoder
from collections import OrderedDict

class JsonUnmarshaler(object):
    def __init__(self):
        self.decoder = Decoder()

    def load(self, stream):
        return self.decoder.decode(json.load(stream, object_pairs_hook=OrderedDict))

class MsgPackUnmarshaler(object):
    def __init__(self):
        self.decoder = Decoder()

    def load(self, stream):
        return self.decoder.decode(msgpack.load(stream, object_pairs_hook=OrderedDict))

