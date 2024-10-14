"""Configurations and utilities for all tests."""

import pytest


def pytest_addoption(parser):
    """Define custom CLI options for `pytest`."""
    parser.addoption(
        "--smoke-tests-only",
        action="store_true",
        default=False,
        help="Run the minimum number of (unit) tests to achieve full coverage",
    )


def pytest_configure(config):
    """Define custom markers explicitly."""
    config.addinivalue_line(
        "markers",
        "integration_test: non-unit test case; skipped during coverage reporting",
    )
    config.addinivalue_line(
        "markers",
        "overlapping_test: test case not contributing towards higher coverage",
    )
    config.addinivalue_line(
        "markers",
        "sanity_test: test case providing confidence in the test data",
    )


def pytest_collection_modifyitems(config, items):
    """Pre-process the test cases programatically.

    - Add `no_cover` marker to test cases with any of these markers:
      + "integration_test"
      + "overlapping_test"
      + "sanity_test"
    - Select test cases with none of the above markers as smoke tests,
      i.e., the minimum number of test cases to achieve 100% coverage
    """
    smoke_tests = []

    for item in items:
        if (
            "integration_test" in item.keywords
            or "overlapping_test" in item.keywords
            or "sanity_test" in item.keywords
        ):
            item.add_marker(pytest.mark.no_cover)

        elif config.getoption("--smoke-tests-only"):
            smoke_tests.append(item)

    if config.getoption("--smoke-tests-only"):
        if not smoke_tests:
            pytest.exit("No smoke tests found")

        items[:] = smoke_tests
