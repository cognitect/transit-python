## Copyright (c) Cognitect, Inc.
## All rights reserved.

# Hash that looks up class keys with inheritance.
import collections

class ClassDict(collections.MutableMapping):
    """A dictionary that looks up class keys with inheritance"""

    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))

    def __getitem__(self, key):
        key = isinstance(key, type) and key or type(key)
        types = key.mro()
        for t in types:
            value = t in self.store and self.store[t]
            if value:
                return value
        raise KeyError("No handler found for: " + str(key))
        return None

    def __setitem__(self, key, value):
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)