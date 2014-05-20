from transit.reader import JsonUnmarshaler
import time
def run_tests():
    t = time.time()
    with open("../transit/seattle-data0.tjs", 'r') as stream:
        data = JsonUnmarshaler().load(stream)
    print "Done: " + str((time.time() - t) * 1000.0)


for x in range(100):
    run_tests()


