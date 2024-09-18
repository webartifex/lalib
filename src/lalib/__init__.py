"""A Python library to study linear algebra.

First, verify that your installation of `lalib` works:
>>> import lalib
>>> lalib.__version__ != '0.0.0'
True

`lalib` exposes its very own "words" (i.e., its public API) at the root
of the package. They can be imported all at once with:

>>> from lalib import *

In addition to Python's built-in numbers, `lalib` comes with a couple of
specific numeric data types, for example, `one` and `zero` representing
the two elements of the Galois field `GF2`:

>>> one + one
zero
>>> one + zero
one
"""

from importlib import metadata

from lalib.elements import gf2


try:
    pkg_info = metadata.metadata(__name__)

except metadata.PackageNotFoundError:
    __author__ = "unknown"
    __pkg_name__ = "unknown"
    __version__ = "unknown"

else:
    __author__ = pkg_info["author"]
    __pkg_name__ = pkg_info["name"]
    __version__ = pkg_info["version"]
    del pkg_info


GF2, one, zero = gf2.GF2, gf2.one, gf2.zero


del gf2
del metadata


__all__ = (
    "GF2",
    "one",
    "zero",
)
