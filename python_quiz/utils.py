import time

def now() -> float:
    """High-resolution timer start."""
    return time.perf_counter()

def seconds(t0: float, t1: float) -> float:
    """Elapsed seconds rounded to milliseconds."""
    return round(t1 - t0, 3)
