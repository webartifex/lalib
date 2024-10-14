"""Utilities to test the `lalib.fields` sub-package."""

import decimal
import fractions
import os

import pytest

from lalib import elements
from lalib import fields
from tests import utils as root_utils


ALL_FIELDS = (fields.Q, fields.R, fields.C, fields.GF2)
NON_10_FIELDS = (fields.Q, fields.R, fields.C)

ONES = (
    1,
    1.0,
    fractions.Fraction(1, 1),
    decimal.Decimal("1.0"),
    elements.one,
    True,
)

ZEROS = (
    0,
    0.0,
    fractions.Fraction(0, 1),
    decimal.Decimal("+0.0"),
    decimal.Decimal("-0.0"),
    elements.zero,
    False,
)

ONES_N_ZEROS = ONES + ZEROS

NON_ONES_N_ZEROS = (
    +42,
    +42.0,
    fractions.Fraction(+42, 1),
    decimal.Decimal("+42.0"),
    -42,
    -42.0,
    fractions.Fraction(-42, 1),
    decimal.Decimal("-42.0"),
)

NUMBERS = ONES_N_ZEROS + NON_ONES_N_ZEROS

DEFAULT_THRESHOLD = root_utils.DEFAULT_THRESHOLD
WITHIN_THRESHOLD = root_utils.WITHIN_THRESHOLD
NOT_WITHIN_THRESHOLD = root_utils.NOT_WITHIN_THRESHOLD

N_RANDOM_DRAWS = os.environ.get("N_RANDOM_DRAWS") or 1


def is_field_element(field, value):
    """Utility method to avoid redundant logic in tests."""
    element = field.cast(value)

    assert element == value
    assert field.validate(value)


def is_not_field_element(field, value):
    """Utility method to avoid redundant logic in tests."""
    with pytest.raises(ValueError, match="not an element of the field"):
        field.cast(value)

    assert not field.validate(value)
    assert not field.validate(value, silent=True)

    with pytest.raises(ValueError, match="not an element of the field"):
        field.validate(value, silent=False)
