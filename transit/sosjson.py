# Ugly streamer
from copy import copy
import json

SKIP = [" ", "\n", "\t"]
ESCAPE = "\\"

def read_chunk(stream):
    """Ignore whitespace outside of strings.
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

def items(stream):
    for s in yield_json(stream):
        yield json.loads(s)

def yield_json(stream):
    buff = u""
    arr_count = 0
    obj_count = 0
    while True:
        buff += read_chunk(stream)

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
