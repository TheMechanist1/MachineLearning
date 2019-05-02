import time
regions = []

enable = False
#profiler to help me with optimization pls ignore
class Region:
    def __init__(self, name):
        self.name = name
        self.time = time.perf_counter()

def start(name):
    if enable:
        regions.append(Region(name))

def end():
    if enable:
        region = regions.pop()
        endTime = time.perf_counter()
        t = endTime - region.time
        print("[profiler] region %s took %s seconds" % (region.name, t))
