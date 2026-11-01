"""Pure simulation helpers, independent of GTK or a particular scene."""
import math

def smooth(value):
    value=max(0.,min(1.,value))
    return value*value*(3-2*value)


def validate_elapsed(elapsed):
    if not math.isfinite(elapsed) or elapsed < 0:
        raise ValueError('Invalid elapsed time')
    return elapsed
