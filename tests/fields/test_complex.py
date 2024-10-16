"""Tests for the `lalib.fields.complex_.ComplexField` only."""

import random

import pytest

from lalib import fields
from tests.fields import utils


# None of the test cases below contributes towards higher coverage
pytestmark = pytest.mark.overlapping_test


C = fields.C


class TestCastAndValidateFieldElements:
    """Test specifics for `C.cast()` and `C.validate()`."""

    @pytest.mark.parametrize("pre_value", [1, 0, +42, -42])
    def test_complex_number_is_field_element(self, pre_value):
        """`C` must be able to process `complex` numbers."""
        value = complex(pre_value, 0)
        utils.is_field_element(C, value)

    @pytest.mark.parametrize("pre_value", ["NaN", "+inf", "-inf"])
    def test_non_finite_complex_number_is_not_field_element(self, pre_value):
        """For now, we only allow finite numbers as field elements.

        This also holds true for `complex` numbers
        with a non-finite `.real` part.
        """
        value = complex(pre_value)
        utils.is_not_field_element(C, value)


class TestIsZero:
    """Test specifics for `C.zero` and `C.is_zero()`."""

    def test_is_almost_zero(self):
        """`value` is within an acceptable threshold of `C.zero`."""
        value = 0.0 + utils.WITHIN_THRESHOLD

        assert pytest.approx(C.zero, abs=utils.DEFAULT_THRESHOLD) == value
        assert C.is_zero(value)

    def test_is_slightly_not_zero(self):
        """`value` is not within an acceptable threshold of `C.zero`."""
        value = 0.0 + utils.NOT_WITHIN_THRESHOLD

        assert pytest.approx(C.zero, abs=utils.DEFAULT_THRESHOLD) != value
        assert not C.is_zero(value)


class TestIsOne:
    """Test specifics for `C.one` and `C.is_one()`."""

    def test_is_almost_one(self):
        """`value` is within an acceptable threshold of `C.one`."""
        value = 1.0 + utils.WITHIN_THRESHOLD

        assert pytest.approx(C.one, abs=utils.DEFAULT_THRESHOLD) == value
        assert C.is_one(value)

    def test_is_slightly_not_one(self):
        """`value` is not within an acceptable threshold of `C.one`."""
        value = 1.0 + utils.NOT_WITHIN_THRESHOLD

        assert pytest.approx(C.one, abs=utils.DEFAULT_THRESHOLD) != value
        assert not C.is_one(value)


@pytest.mark.repeat(utils.N_RANDOM_DRAWS)
class TestDrawRandomFieldElement:
    """Test specifics for `C.random()`."""

    def test_draw_elements_with_custom_bounds(self):
        """Draw a random element from `C` ...

        ... within the bounds passed in as arguments.

        For `C`, the bounds are interpreted in a 2D fashion.
        """
        lower = complex(
            200 * random.random() - 100,  # noqa: S311
            200 * random.random() - 100,  # noqa: S311
        )
        upper = complex(
            200 * random.random() - 100,  # noqa: S311
            200 * random.random() - 100,  # noqa: S311
        )

        element = C.random(lower=lower, upper=upper)

        l_r, u_r = min(lower.real, upper.real), max(lower.real, upper.real)
        l_i, u_i = min(lower.imag, upper.imag), max(lower.imag, upper.imag)

        assert l_r <= element.real <= u_r
        assert l_i <= element.imag <= u_i
