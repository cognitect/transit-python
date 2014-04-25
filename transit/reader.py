## Copyright (c) Cognitect, Inc.
## All rights reserved.


import simplejson
import transit_types
import iso8601
import uuid
class Cache(object):
    def __init__(self):
        self.idx = 0
        self.cache = [None] * 94
    def cache_tag(self, itm):
        self.cache[self.idx] = itm
        self.idx += 1
        if self.idx == len(self.cache):
            self.idx = 0

    def __getitem__(self, char):
        idx = ord(char) - 33
        return self.cache[idx]


def parse_value(itm, cache):
    if isinstance(itm, list):
        return parse_vector(itm, cache)

    elif isinstance(itm, dict):
        if len(itm) == 1:
            key = itm.keys()[0]
            if key.startswith("~#"):
                tag = key[2:]
                cache.cache_tag(tag)
                try:
                    parser = tag_parsers[tag]
                except KeyError:
                    raise Exception("No tag parser for " + str(key))

                return parser(itm[key], cache)
            elif key.startswith("^"):
                tag = cache[key[1]]
                parser = tag_parsers[tag]
                return parser(itm[key], cache)
            assert False, key
        return parse_map(itm, cache)
    elif isinstance(itm, str):
        return parse_string(itm, cache)

    return itm

def parse_map(itm, cache):
    acc = []
    for key in itm:
        acc.append(parse_value(key, cache))
        acc.append(parse_value(itm[key], cache))

    return transit_types.CMap(acc)

def parse_cmap(itm, cache):
    data = map(lambda x: parse_value(x, cache), itm)
    return transit_types.CMap(data)


def parse_set(itm, cache):
    data = map(lambda x: parse_value(x, cache), itm)
    return transit_types.Set(data)

def parse_string(itm, cache):
    if itm[0] == "~":
        tag = itm[1]
        try:
            parser = tag_parsers[tag]
        except KeyError as ex:
            raise Exception("No tag parser for " + itm)

        return parser(itm[2:], cache)
    return itm

def parse_array(itm, cache):
    return transit_types.Array(map(lambda x: parse_value(x, cache), itm))

def parse_list(itm, cache):
    return transit_types.List(map(lambda x: parse_value(x, cache), itm))

def parse_vector(itm, cache):
    return transit_types.Vector(map(lambda x: parse_value(x, cache), itm))

def parse_keyword(itm, cache):
    return transit_types.kws(itm)

def parse_date(itm, cache):
    return iso8601.parse_date(itm)

def parse_uuid(item, cache):
    return uuid.UUID(item)

def parse_uri(item, cache):
    return transit_types.URI(item)

tag_parsers = {"'": lambda x, c: parse_value(x, c),
               "~": lambda x, c: "~" + x,
               "^": lambda x, c: "^" + x,
               ":": parse_keyword,
               "$": lambda x, c: transit_types.Symbol(x),
               "i": lambda x, c: int(x),
               "t": parse_date,
               "u": parse_uuid,
               "r": parse_uri,
               "set": parse_set,
               "c": lambda x, c: x,
               "list": parse_list,
               "cmap": parse_cmap}


def unmarshal(fp):
    data = simplejson.load(fp)
    return parse_value(data, Cache())