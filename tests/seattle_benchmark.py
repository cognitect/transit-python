## Copyright 2014 Cognitect. All Rights Reserved.
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS-IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

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

means = {}
for jsonfile in ["../transit/seattle-data0.json", "../transit/seattle-data0.jsonv"]:
    fd = open(jsonfile, 'r')
    data = fd.read()
    fd.close()

    print("-"*50)
    print("Running " + jsonfile)
    print("-"*50)

    runs = 100
    deltas = [run_tests(data) for x in range(runs)]
    means[jsonfile] = sum(deltas)/runs

for jsonfile, mean in means.items():
    print "\nMean for" + jsonfile + ": "+str(mean)

