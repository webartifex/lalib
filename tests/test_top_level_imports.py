"""Test top-level imports for `lalib`."""

import lalib as top_level


def test_top_level_imports():
    """Verify `from lalib import *` works."""
    environment = {}

    exec("...", environment, environment)  # noqa: S102
    defined_vars_before = set(environment)

    exec("from lalib import *", environment, environment)  # noqa: S102
    defined_vars_after = set(environment)

    new_vars = defined_vars_after - defined_vars_before

    assert new_vars == set(top_level.__all__)
