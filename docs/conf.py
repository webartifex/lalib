"""Configure sphinx."""

import lalib


project = lalib.__pkg_name__
author = lalib.__author__
project_copyright = f"2024, {author}"
version = release = lalib.__version__

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
]
