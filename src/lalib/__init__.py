"""Source code for the educational `lalib` library.

The goal of this library is to serve as a resource for software engineers
and data scientists to learn about linear algebra via reading and writing code.
"""

from importlib import metadata as _metadata


try:
    _pkg_info = _metadata.metadata(__name__)

except _metadata.PackageNotFoundError:  # pragma: no cover
    __pkg_name__ = 'unknown'
    __version__ = 'unknown'

else:
    __pkg_name__ = _pkg_info['name']
    __version__ = _pkg_info['version']
