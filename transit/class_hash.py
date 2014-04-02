# Hash that looks up class keys with inheritance.

class ClassHash:
  def __init__(self):
    print "init"
    self.values = {}

  def put(self, typ, value):
    self.values[typ] = value

  def get(self, typ):
    types = typ.mro()
    for t in types:
      value = self.values.get(t)
      if value:
        return value
    return None
