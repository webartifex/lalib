"""Various elements of various fields.

Import the objects like so:

>>> from lalib.elements import *

Then, use them:

>>> one + zero
one

>>> GF2(0)
zero
>>> GF2(42)
Traceback (most recent call last):
...
ValueError: ...
>>> GF2(42, strict=False)
one
"""

from lalib.elements import gf2


GF2, one, zero = gf2.GF2, gf2.one, gf2.zero

del gf2


__all__ = (
    "GF2",
    "one",
    "zero",
)
