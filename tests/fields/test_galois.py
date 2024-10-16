"""Tests for the `lalib.fields.galois.GaloisField2` only."""

import itertools

import pytest

from lalib import fields
from tests.fields import utils


# None of the test cases below contributes towards higher coverage
pytestmark = pytest.mark.overlapping_test


GF2 = fields.GF2


class TestCastAndValidateFieldElements:
    """Test specifics for `GF2.cast()` and `GF2.validate()`."""

    @pytest.mark.parametrize("value", utils.NUMBERS)
    def test_number_is_field_element(self, value):
        """Common numbers are always `GF2` elements in non-`strict` mode."""
        left = GF2.cast(value, strict=False)
        right = bool(value)

        assert left == right
        assert GF2.validate(value, strict=False)

    @pytest.mark.parametrize("value", utils.ONES_N_ZEROS)
    def test_one_and_zero_number_is_field_element(self, value):
        """`1`-like and `0`-like `value`s are `GF2` elements."""
        utils.is_field_element(GF2, value)

    @pytest.mark.parametrize("pre_value", [1, 0])
    def test_one_or_zero_like_complex_number_is_field_element(self, pre_value):
        """`GF2` can process `complex` numbers."""
        value = complex(pre_value, 0)
        utils.is_field_element(GF2, value)

    @pytest.mark.parametrize("pre_value", [+42, -42])
    def test_non_one_or_zero_like_complex_number_is_not_field_element(self, pre_value):
        """`GF2` can process `complex` numbers ...

        ... but they must be `one`-like or `zero`-like
        to become a `GF2` element.
        """
        value = complex(pre_value, 0)
        utils.is_not_field_element(GF2, value)

    @pytest.mark.parametrize("pre_value", [+42, -42])
    def test_non_one_or_zero_like_complex_number_is_field_element(self, pre_value):
        """`GF2` can process all `complex` numbers in non-`strict` mode."""
        value = complex(pre_value, 0)

        left = GF2.cast(value, strict=False)
        right = bool(value)

        assert left == right
        assert GF2.validate(value, strict=False)

    @pytest.mark.parametrize("pre_value", ["NaN", "+inf", "-inf"])
    def test_non_finite_complex_number_is_not_field_element(self, pre_value):
        """For now, we only allow finite numbers as field elements.

        This also holds true for `complex` numbers
        with a non-finite `.real` part.
        """
        value = complex(pre_value)
        utils.is_not_field_element(GF2, value)

    @pytest.mark.parametrize("value", ["1", "0"])
    def test_one_or_zero_like_numeric_str_is_field_element(self, value):
        """`GF2` can process `str`ings resemling `1`s and `0`s."""
        utils.is_field_element(GF2, value)

    @pytest.mark.parametrize("value", ["+42", "-42"])
    def test_non_one_or_zero_like_numeric_str_is_not_field_element(self, value):
        """`GF2` can process `str`ings resembling numbers ...

        ... but they must be `1`-like or `0`-like.
        """
        utils.is_not_field_element(GF2, value)

    @pytest.mark.parametrize("value", ["+42", "-42"])
    def test_non_one_or_zero_like_numeric_str_is_field_element(self, value):
        """`GF2` can process `str`ings resemling any number in non-`strict` mode."""
        left = GF2.cast(value, strict=False)
        right = bool(float(value))

        assert left == right
        assert GF2.validate(value, strict=False)

    @pytest.mark.parametrize("value", ["NaN", "+inf", "-inf"])
    def test_non_finite_numeric_str_is_not_field_element(self, value):
        """`GF2` can process `str`ings resemling numbers ...

        ... but they must represent finite numbers.
        """
        utils.is_not_field_element(GF2, value)


class TestIsZero:
    """Test specifics for `GF2.zero` and `GF2.is_zero()`."""

    def test_is_slightly_not_zero(self):
        """`value` is not within an acceptable threshold of `GF2.zero`."""
        value = 0.0 + utils.NOT_WITHIN_THRESHOLD

        assert GF2.zero != value

        with pytest.raises(ValueError, match="not an element of the field"):
            GF2.is_zero(value)


class TestIsOne:
    """Test specifics for `GF2.one` and `GF2.is_one()`."""

    def test_is_slightly_not_one(self):
        """`value` is not within an acceptable threshold of `GF2.one`."""
        value = 1.0 + utils.NOT_WITHIN_THRESHOLD

        assert GF2.one != value

        with pytest.raises(ValueError, match="not an element of the field"):
            GF2.is_one(value)


@pytest.mark.repeat(utils.N_RANDOM_DRAWS)
class TestDrawRandomFieldElement:
    """Test specifics for `GF2.random()`."""

    @pytest.mark.parametrize("bounds", itertools.product([0, 1], repeat=2))
    def test_draw_element_with_custom_bounds(self, bounds):
        """Draw a random element from `GF2` in non-`strict` mode ...

        ... within the bounds passed in as arguments.
        """
        lower, upper = bounds
        element = GF2.random(lower=lower, upper=upper)

        if upper < lower:
            lower, upper = upper, lower

        assert lower <= element <= upper
