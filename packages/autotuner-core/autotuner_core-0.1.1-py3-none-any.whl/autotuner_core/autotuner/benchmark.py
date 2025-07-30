import time


def benchmark(func, *args, **kwargs):
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    duration_ms = round((end - start) * 1000, 4)
    return result, duration_ms
