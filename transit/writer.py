## Copyright (c) Cognitect, Inc.
## All rights reserved.

import msgpack
import class_hash
improt transit_types

ESC = '~'
SUB = '^'
RESERVED = '`'

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

class MessagePackMarshaler:
  def __init__(self, io):
    self.io = io
    self.packer = msgpack.Packer()
    self.handlers = Handler()

  def marshal(self, obj, as_map_key, cache):
    print 'Marshal', obj

    handler = self.handlers.get(obj)
    print 'Handler:', handler
    tag = handler.tag(obj)
    if(as_map_key):
      rep = handler.string_rep(obj)
    else:
      rep = handler.rep(obj)

    print 'tag =', tag

    if tag == 's':
      self.emit_string('', '', rep, as_map_key, cache)
    elif tag == 'i':
      self.emit_int(rep, as_map_key, cache)
    elif tag == 'd':
      self.emit_double(rep, as_map_key, cache)
    elif tag == '_':
      self.emit_none(rep, as_map_key, cache)
    elif tag == '?':
      self.emit_boolean(rep, as_map_key, cache)
    elif tag == 'array':
      self.emit_array(rep, as_map_key, cache)
    elif tag == 'map':
      self.emit_map(rep, as_map_key, cache)
    else:
      self.emit_encoded(tag, obj, as_map_key, cache)

  def emit_array(self, a, _, cache):
    self.io.write(self.packer.pack_array_header(len(a)))
    for item in a:
      self.marshal(item, False, cache)

  def emit_map(self, m, _, cache):
    self.io.write(self.packer.pack_map_header(len(m)))
    for k in m:
      self.marshal(k, True, cache)
      self.marshal(m[k], False, cache)

  def emit_int(self, i, as_map_key, cache):
    print 'emit_int::', i
    packed = self.packer.pack(i)
    self.io.write(packed)

  def emit_string(self, prefix, tag, string, as_map_key, cache):
    print('emit_string::', prefix, tag, string)
    packed = self.packer.pack(prefix + tag + self.escape(string))
    self.io.write(packed)

  def emit_none(self, _, as_map_key, cache):
    if(as_map_key):
      self.emit_string(ESC, '_', '', True, cache)
    else:
      self.io.write(self.packer.pack(None))

  def emit_boolean(self, b, as_map_key, cache):
    if as_map_key:
      self.emit_string(ESC, '_', b, True, cache)
    else:
      self.io.write(self.packer.pack(b))

  def escape(self, s):
    if (s == None) or (s == True) or (s == False):
      return s
    elif len(s) > 0:
      ch = s[0]
      if (ch == ESC) or (ch == SUB) or (ch == RESERVED):
        return ESC + s
    return s


#f = open('stuff.mp', 'w')
#mpm = MessagePackMarshaler(f)
#mpm.marshal({'aaa': 9, 'bbb': 10, 'ccc': 11}, False, None)
#mpm.marshal([1,2,3,4], False, None)
#mpm.marshal(None, False, None)
#mpm.marshal(False, False, None)
#mpm.marshal(True, False, None)
#
#mpm.marshal(None, True, None)
#mpm.marshal(False, True, None)
#mpm.marshal(True, True, None)
