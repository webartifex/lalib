"""A collection of common fields used in linear algebra."""

from lalib.fields import base
from lalib.fields import complex_
from lalib.fields import galois
from lalib.fields import rational
from lalib.fields import real
from lalib.fields import utils


Field = base.Field

Q = rational.Q
R = real.R
C = complex_.C
GF2 = galois.GF2


del base
del complex_
del galois
del rational
del real
del utils  # `import`ed and `del`eted to not be in the final namespace


__all__ = (
    "Q",
    "R",
    "C",
    "GF2",
)
