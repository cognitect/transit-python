import simplejson
import transit_types



def parse_value(itm):
    if isinstance(itm, list):
        return parse_array(itm)

    elif isinstance(itm, dict):
        if len(itm) == 1:
            key = itm.keys()[0]
            if key.startswith("~#"):
                tag = key[2:]
                try:
                    parser = tag_parsers[tag]
                except KeyError as ex:

                    raise Exception("No tag parser for " + str(key))

                return parser(itm[key])
        return parse_map(itm)

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
    return transit_types.Set(acc)

def parse_array(itm):
    return transit_types.Vector(map(parse_value, itm))

def parse_list(itm):
    return transit_types.Vector(map(parse_value, itm))

tag_parsers = {"'": lambda x: x,
               "set": parse_set,
               "c": lambda x: x,
               "list": lambda x: tuple,
               "cmap": parse_cmap}


def unmarshal(fp):
    data = simplejson.load(fp)
    return parse_value(data)