"""Test top-level imports for `lalib`."""

import importlib
from typing import Any

import pytest


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "path_to_package",
    [
        "lalib",
        "lalib.elements",
    ],
)
def test_top_level_imports(path_to_package: str):
    """Verify `from {path_to_package} import *` works."""
    package = importlib.import_module(path_to_package)

    environment: dict[str, Any] = {}

    exec("...", environment, environment)  # noqa: S102
    defined_vars_before = set(environment)

    exec(f"from {path_to_package} import *", environment, environment)  # noqa: S102
    defined_vars_after = set(environment)

    new_vars = defined_vars_after - defined_vars_before

    assert new_vars == set(package.__all__)
