from constants import *


class NoneHandler:
  def tag(self, _):
    return '_'
  def rep(self, _):
    return None
  def string_rep(self, n):
    return None

class IntHandler:
  def tag(self, i):
    return 'i'
  def rep(self, i):
    return i
  def string_rep(self, i):
    return str(i)

class StringHandler:
  def tag(self, s):
    return 's'
  def rep(self, s):
    return s
  def string_rep(self, s):
    return s

class BooleanHandler:
  def tag(self, _):
    return '?'
  def rep(self, b):
    return b
  def string_rep(self, b):
    if b:
      return 't'
    else:
      return 'f'

class ArrayHandler:
  def tag(self, a):
    return 'array'
  def rep(self, a):
    return a
  def string_rep(self, a):
    return None

class MapHandler:
  def tag(self, m):
    return 'map'
  def rep(self, m):
    return m
  def string_rep(self, m):
    return None


class Handler:
  def __init__(self):
    self.handlers = class_hash.ClassHash()
    self.handlers.put(type(None), NoneHandler())
    self.handlers.put(type(True), BooleanHandler())
    self.handlers.put(str, StringHandler())
    self.handlers.put(list, ArrayHandler())
    self.handlers.put(dict, MapHandler())
    self.handlers.put(int, IntHandler())

  def get(self, obj):
    return self.handlers.get(obj.__class__)