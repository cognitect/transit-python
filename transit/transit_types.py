class Keyword(object):
    def __init__(self, value):
        assert isinstance(value, str)
        self.str = value

    def __eq__(self, other):
        return self is other

    def __call__(self, mp):
        return mp[self]

    def __repr__(self):
        return ":" + self.str

    def __str__(self):
        return ":" + self.str

kw_cache = {}

class _KWS(object):
    def __getattr__(self, item):
        value = self(item)
        setattr(self, item, value)
        return value

    def __call__(self, str):
        if str in kw_cache:
            return kw_cache[str]
        else:
            kw_cache[str] = Keyword(str)
            return kw_cache[str]

kws = _KWS()
