import simplejson
import transit_types

class Cache(object):
    def __init__(self):
        self.idx = 0
        self.cache
    def cache_tag(self, itm):


    def reset_cache():


def parse_value(itm):
    if isinstance(itm, list):
        return parse_array(itm)

    elif isinstance(itm, dict):
        if len(itm) == 1:
            key = itm.keys()[0]
            if key.startswith("~#"):
                tag = key[2:]
                cache_tag(tag)
                try:
                    parser = tag_parsers[tag]
                except KeyError as ex:

                    raise Exception("No tag parser for " + str(key))

                return parser(itm[key])
            assert False, key
        return parse_map(itm)
    elif isinstance(itm, str):
        return parse_string(itm)

    return itm

def parse_map(itm):
    acc = {}
    for key in itm:
        acc[parse_value(key)] = parse_value(itm[key])

    return acc

def parse_cmap(itm):
    acc = {}
    i = iter(itm)
    try:
        while True:
            key = i.next()
            value = i.next()
            acc[parse_value(key)] = parse_value(value)
    except StopIteration:
        return transit_types.Dict(**acc)

def parse_set(itm):
    acc = []
    for i in itm:
        acc.append(parse_value(i))
    print itm
    return transit_types.Set(acc)

def parse_string(itm):
    if itm[0] == "~":
        tag = itm[1]
        try:
            parser = tag_parsers[tag]
        except KeyError as ex:
            raise Exception("No tag parser for " + itm)

        return parser(itm[2:])
    return itm

def parse_array(itm):
    return transit_types.Vector(map(parse_value, itm))

def parse_list(itm):
    return transit_types.Vector(map(parse_value, itm))

def parse_keyword(itm):
    return transit_types.kws(itm)

tag_parsers = {"'": lambda x: x,
               "~": lambda x: "~" + x,
               "^": lambda x: "^" + x,
               ":": parse_keyword,
               "$": transit_types.Symbol,
               "i": int,
               "set": parse_set,
               "c": lambda x: x,
               "list": parse_list,
               "cmap": parse_cmap}


def unmarshal(fp):
    data = simplejson.load(fp)
    return parse_value(data)