"""A Python library to study linear algebra.

First, verify that your installation of `lalib` works:
>>> import lalib
>>> lalib.__version__ != '0.0.0'
True
"""

from importlib import metadata


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


del metadata
