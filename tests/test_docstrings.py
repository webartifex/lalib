"""Integrate `xdoctest` into the test suite.

Ensure all code snippets in docstrings are valid and functioning code.

Important: All modules with docstrings containing code snippets
           must be put on the parameter list below by hand!
"""

import pytest
import xdoctest


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "module",
    [
        "lalib",
        "lalib.elements",
        "lalib.elements.galois",
        "lalib.fields",
        "lalib.fields.base",
        "lalib.fields.complex_",
        "lalib.fields.galois",
        "lalib.fields.rational",
        "lalib.fields.real",
    ],
)
def test_docstrings(module):
    """Test code snippets within the package with `xdoctest`."""
    result = xdoctest.doctest_module(module, "all")

    assert result["n_failed"] == 0
