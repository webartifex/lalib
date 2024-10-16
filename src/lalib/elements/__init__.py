"""Various elements of various fields.

Import the objects like so:

>>> from lalib.elements import *

Then, use them:

>>> one + zero
one
>>> one + one
zero

>>> type(one)
gf2

The `gf2` type is similar to the built-in `bool`.
To cast objects as `gf2` values:

>>> gf2(0)
zero
>>> gf2(1)
one

>>> gf2(42)
one
>>> gf2(-42)
one

Yet, there is also a `strict` mode where values
not equal to `1` or `0` within a `threshold` are not accepted.

>>> gf2(42, strict=True)
Traceback (most recent call last):
...
ValueError: ...
"""

from lalib.elements import galois


gf2, one, zero = galois.gf2, galois.one, galois.zero

del galois


__all__ = (
    "gf2",
    "one",
    "zero",
)
