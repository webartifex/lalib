"""Various elements of various fields.

Import the objects like so:

>>> from lalib.elements import *

Then, use them:

>>> one + zero
one

>>> gf2(0)
zero
>>> gf2(42)
Traceback (most recent call last):
...
ValueError: ...
>>> gf2(42, strict=False)
one
"""

from lalib.elements import galois


gf2, one, zero = galois.gf2, galois.one, galois.zero

del galois


__all__ = (
    "gf2",
    "one",
    "zero",
)
