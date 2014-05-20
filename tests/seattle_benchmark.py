## Copyright (c) Cognitect, Inc.
## All rights reserved.

from transit.reader import JsonUnmarshaler
import time
from StringIO import StringIO
def run_tests(data):
    t = time.time()
    JsonUnmarshaler().load(StringIO(data))
    print "Done: " + str((time.time() - t) * 1000.0)

data = open("../transit/seattle-data0.tjs", 'r').read()

for x in range(100):
    run_tests(data)


