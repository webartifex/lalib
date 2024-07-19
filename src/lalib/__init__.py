"""Source code for the lalib educational library.

The goal of this library is to serve as a resource for software engineers
and data scientists to learn about linear algebra via reading and writing code.

Example:
    >>> import lalib
    >>> lalib.__version__ != '0.0.0'
    True
"""

try:
    from importlib import metadata as _metadata
except ImportError:  # pragma: no cover
    import importlib_metadata as _metadata  # type:ignore


try:
    _pkg_info = _metadata.metadata(__name__)

except _metadata.PackageNotFoundError:  # pragma: no cover
    __author__ = 'unknown'
    __pkg_name__ = 'unknown'
    __version__ = 'unknown'

else:
    __author__ = _pkg_info['author']
    __pkg_name__ = _pkg_info['name']
    __version__ = _pkg_info['version']
