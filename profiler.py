import time
regions = []

enable = False

class Region:
    def __init__(self, name):
        self.name = name
        self.time = time.perf_counter()

def profileStart(name):
    if enable:
        regions.append(Region(name))

def profileEnd():
    if enable:
        region = regions.pop()
        endTime = time.perf_counter()
        t = endTime - region.time
        print("[profiler] region %s took %s seconds" % (region.name, t))
