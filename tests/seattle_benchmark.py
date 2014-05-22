## Copyright (c) Cognitect, Inc.
## All rights reserved.

from transit.reader import JsonUnmarshaler
import json
import time
from StringIO import StringIO
def run_tests(data):
    datas = StringIO(data)
    t = time.time()
    JsonUnmarshaler().load(datas)
    et = time.time()
    datas = StringIO(data)
    tt = time.time()
    json.load(datas)
    ett = time.time()
    print "Done: " + str((et - t) * 1000.0) + "  --  raw JSON in: " + str((ett - tt) * 1000.0)

fd = open("../transit/seattle-data0.tjs", 'r')
data = fd.read()
fd.close()

for x in range(100):
    run_tests(data)

