import bisect
import random
import time
from .haren import HAREN

def linear_search(arr, target):
    for i, v in enumerate(arr):
        if v == target:
            return i
    return -1

def run_benchmark(array_size=100_000, trials=100):
    arr_unsorted = random.sample(range(array_size * 10), array_size)
    arr_sorted = sorted(arr_unsorted)
    targets = random.choices(arr_unsorted, k=trials)

    haren = HAREN(arr_sorted)
    start = time.time()
    for t in targets:
        i = haren.search(t)
        assert i != -1 and haren.arr[i] == t
    haren_time = time.time() - start

    start = time.time()
    for t in targets:
        i = bisect.bisect_left(arr_sorted, t)
        assert arr_sorted[i] == t
    binary_time = time.time() - start

    start = time.time()
    for t in targets:
        assert linear_search(arr_unsorted, t) != -1
    linear_time = time.time() - start

    return {
        'size': array_size,
        'haren': haren_time,
        'binary': binary_time,
        'linear': linear_time
    }
