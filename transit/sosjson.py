# copyright 2014 cognitect. all rights reserved.
#
# licensed under the apache license, version 2.0 (the "license");
# you may not use this file except in compliance with the license.
# you may obtain a copy of the license at
#
#      http://www.apache.org/licenses/license-2.0
#
# unless required by applicable law or agreed to in writing, software
# distributed under the license is distributed on an "as-is" basis,
# without warranties or conditions of any kind, either express or implied.
# see the license for the specific language governing permissions and
# limitations under the license.

# Simple object streaming in Python - just reads one complete JSON object
# at a time and returns json.loads of that string.

# Ugly implementation at moment
from copy import copy
import json

SKIP = [" ", "\n", "\t"]
ESCAPE = "\\"


def read_chunk(stream):
    """Ignore whitespace outside of strings. If we hit a string, read it in
    its entirety.
    """
    chunk = stream.read(1)
    while chunk in SKIP:
        chunk = stream.read(1)
    if chunk == "\"":
        chunk += stream.read(1)
        while not chunk.endswith("\""):
            if chunk[-1] == ESCAPE:
                chunk += stream.read(2)
            else:
                chunk += stream.read(1)
    return chunk


def items(stream, **kwargs):
    """External facing items. Will return item from stream as available.
    Currently waits in loop waiting for next item. Can pass keywords that
    json.loads accepts (such as object_pairs_hook)
    """
    for s in yield_json(stream):
        yield json.loads(s, **kwargs)


def yield_json(stream):
    """Uses array and object delimiter counts for balancing.
    """
    buff = u""
    arr_count = 0
    obj_count = 0
    while True:
        buff += read_chunk(stream)

        # If we finish parsing all objs or arrays, yield a finished JSON
        # entity.
        if buff.endswith('{'):
            obj_count += 1
        if buff.endswith('['):
            arr_count += 1
        if buff.endswith(']'):
            arr_count -= 1
            if obj_count == arr_count == 0:
                json_item = copy(buff)
                buff = u""
                yield json_item
        if buff.endswith('}'):
            obj_count -= 1
            if obj_count == arr_count == 0:
                json_item = copy(buff)
                buff = u""
                yield json_item
