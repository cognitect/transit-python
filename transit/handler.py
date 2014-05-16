from constants import *
from class_hash import ClassDict

class NoneHandler(object):
    @staticmethod
    def tag(_):
        return '_'
    @staticmethod
    def rep(_):
        return None
    @staticmethod
    def string_rep(n):
        return None

class IntHandler(object):
    @staticmethod
    def tag(i):
        return 'i'
    @staticmethod
    def rep(i):
        return i
    @staticmethod
    def string_rep(i):
        return str(i)

class StringHandler(object):
    @staticmethod
    def tag(s):
        return 's'
    @staticmethod
    def rep(s):
        return s
    @staticmethod
    def string_rep(s):
        return s

class BooleanHandler(object):
    @staticmethod
    def tag(_):
        return '?'
    @staticmethod
    def rep(b):
        return b
    @staticmethod
    def string_rep(b):
        return b and 't' or 'f'

class ArrayHandler(object):
    @staticmethod
    def tag(a):
        return 'array'
    @staticmethod
    def rep(a):
        return a
    @staticmethod
    def string_rep(a):
        return None

class MapHandler(object):
    @staticmethod
    def tag(m):
        return 'map'
    @staticmethod
    def rep(m):
        return m
    @staticmethod
    def string_rep(m):
        return None

class Handler(ClassDict):
    def __init__(self):
        super(Handler, self).__init__()
        self.handlers = class_hash.ClassDict()
        self.handlers[type(None)] = NoneHandler
        self.handlers[bool] = BooleanHandler
        self.handlers[str] = StringHandler
        self.handlers[list] = ArrayHandler
        self.handlers[tuple] = ArrayHandler
        self.handlers[dict] = MapHandler
        self.handlers[int] = IntHandler

