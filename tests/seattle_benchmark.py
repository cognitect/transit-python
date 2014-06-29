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
    read_delta = (et - t) * 1000.0
    print "Done: " + str(read_delta) + "  --  raw JSON in: " + str((ett - tt) * 1000.0)
    return read_delta

fd = open("../transit/seattle-data0.tjs", 'r')
data = fd.read()
fd.close()

runs = 100
deltas = [run_tests(data) for x in range(runs)]
print "\nMean: "+str(sum(deltas)/runs)

