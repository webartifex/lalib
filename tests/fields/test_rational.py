"""Tests for the `lalib.fields.rational.RationalField` only."""

import fractions

import pytest

from lalib import fields


# None of the test cases below contributes towards higher coverage
pytestmark = pytest.mark.overlapping_test


Q = fields.Q


class TestCastAndValidateFieldElements:
    """Test specifics for `Q.cast()` and `Q.validate()`."""

    @pytest.mark.parametrize(
        "value",
        ["1", "0", "1/1", "0/1", "+42", "-42", "+42/1", "-42/1"],
    )
    def test_str_is_field_element(self, value):
        """`fractions.Fraction()` also accepts `str`ings.

        Source: https://docs.python.org/3/library/fractions.html#fractions.Fraction
        """
        left = Q.cast(value)
        right = fractions.Fraction(value)

        assert left == right
        assert Q.validate(value)
