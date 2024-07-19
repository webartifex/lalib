"""Configure sphinx."""

import lalib


project = lalib.__pkg_name__
author = lalib.__author__
copyright = f'2020, {author}'  # pylint:disable=redefined-builtin
version = release = lalib.__version__

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
]
