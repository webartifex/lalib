"""Library-wide default settings."""

import math


NDIGITS = 12

THRESHOLD = 1 / (10**NDIGITS)

MAX_DENOMINATOR = math.trunc(1 / THRESHOLD)


del math
