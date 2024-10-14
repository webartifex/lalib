"""Generic tests for all `lalib.fields.*.Field`s.

The abstract base class `lalib.fields.base.Field`
defines generic behavior that all concrete `Field`s
in the `lalib.fields` sub-package must implement.
"""

import random

import pytest

from lalib import fields
from tests.fields import utils


@pytest.mark.parametrize("field", utils.ALL_FIELDS)
class TestGenericClassBehavior:
    """Generic `Field` behavior."""

    def test_create_singletons(self, field):
        """All `field`s so far are singletons."""
        cls = type(field)
        new_field = cls()

        assert new_field is field

    @pytest.mark.parametrize("func", [repr, str])
    def test_text_repr(self, field, func):
        """The text representations behave like Python literals."""
        new_field = eval(func(field), fields.__dict__)  # noqa: S307

        assert new_field is field


class TestCastAndValidateFieldElements:
    """Test `Field.cast()` and `Field.validate()`.

    Every `field` must be able to tell if a given `value` is
    an element of the `field`, and, if so, `.cast()` it as such.
    """

    @pytest.mark.parametrize("field", utils.NON_10_FIELDS)
    @pytest.mark.parametrize("value", utils.NUMBERS)
    def test_number_is_field_element(self, field, value):
        """Common numbers are typically `field` elements.

        This is not true for `GF2`, which, by default,
        only accepts `1`-like and `0`-like numbers.
        """
        utils.is_field_element(field, value)

    @pytest.mark.parametrize("field", utils.ALL_FIELDS)
    @pytest.mark.parametrize("value", utils.ONES_N_ZEROS)
    def test_one_and_zero_number_is_field_element(self, field, value):
        """`1`-like and `0`-like numbers are always `field` elements."""
        utils.is_field_element(field, value)

    @pytest.mark.parametrize("field", utils.ALL_FIELDS)
    @pytest.mark.parametrize("value", ["abc", (1, 2, 3)])
    def test_non_numeric_value_is_not_field_element(self, field, value):
        """Values of non-numeric data types are typically not `field` elements."""
        utils.is_not_field_element(field, value)

    @pytest.mark.parametrize("field", utils.ALL_FIELDS)
    @pytest.mark.parametrize("pre_value", ["NaN", "+inf", "-inf"])
    def test_non_finite_number_is_not_field_element(self, field, pre_value):
        """For now, we only allow finite numbers as `field` elements.

        Notes:
          - `Q._cast_func()` cannot handle non-finite `value`s
            and raises an `OverflowError` or `ValueError`
            => `Field.cast()` catches these errors
               and (re-)raises a `ValueError` instead
            => no need to define a specific `._post_cast_filter()`
          - `R._cast_func()` and `C._cast_func()`
            handle non-finite `value`s without any complaints
            => using a `._post_cast_filter()`, we don't allow
               non-finite but castable `value`s to be `field` elements
          - `GF2._cast_func()` handles non-finite `value`s
             by raising a `ValueError` already
            => `Field.cast()` re-raises it with an adapted message
            => no need to define a specific `._post_cast_filter()`
        """
        value = float(pre_value)
        utils.is_not_field_element(field, value)


class TestDTypes:
    """Test the `Field.dtype` property."""

    @pytest.mark.parametrize("field", utils.ALL_FIELDS)
    def test_field_dtype(self, field):
        """`field.dtype` must be a `type`."""
        assert isinstance(field.dtype, type)

    @pytest.mark.parametrize("field", utils.ALL_FIELDS)
    def test_element_is_instance_of_field_dtype(self, field):
        """Elements are an instance of `field.dtype`."""
        element = field.random()

        assert isinstance(element, field.dtype)

    @pytest.mark.parametrize("field", utils.ALL_FIELDS)
    def test_element_dtype_is_subclass_of_field_dtype(self, field):
        """Elements may have a more specific `.dtype` than their `field.dtype`."""
        element = field.random()
        dtype = type(element)

        assert issubclass(dtype, field.dtype)


class TestIsZero:
    """Test `Field.zero` & `Field.is_zero()`."""

    @pytest.mark.parametrize("field", utils.ALL_FIELDS)
    @pytest.mark.parametrize("value", utils.ZEROS)
    def test_is_exactly_zero(self, field, value):
        """`value` is equal to `field.zero`."""
        assert field.zero == value
        assert field.is_zero(value)

    @pytest.mark.parametrize("field", utils.ALL_FIELDS)
    def test_is_almost_zero(self, field):
        """`value` is within an acceptable threshold of `field.zero`."""
        value = 0.0 + utils.WITHIN_THRESHOLD

        assert pytest.approx(field.zero, abs=utils.DEFAULT_THRESHOLD) == value
        assert field.is_zero(value)

    @pytest.mark.parametrize("field", utils.NON_10_FIELDS)
    def test_is_slightly_not_zero(self, field):
        """`value` is not within an acceptable threshold of `field.zero`."""
        value = 0.0 + utils.NOT_WITHIN_THRESHOLD

        assert pytest.approx(field.zero, abs=utils.DEFAULT_THRESHOLD) != value
        assert not field.is_zero(value)

    @pytest.mark.parametrize("field", utils.ALL_FIELDS)
    @pytest.mark.parametrize("value", utils.ONES)
    def test_is_not_zero(self, field, value):
        """`value` is not equal to `field.zero`."""
        assert field.zero != value
        assert not field.is_zero(value)


class TestIsOne:
    """Test `Field.one` & `Field.is_one()`."""

    @pytest.mark.parametrize("field", utils.ALL_FIELDS)
    @pytest.mark.parametrize("value", utils.ONES)
    def test_is_exactly_one(self, field, value):
        """`value` is equal to `field.one`."""
        assert field.one == value
        assert field.is_one(value)

    @pytest.mark.parametrize("field", utils.ALL_FIELDS)
    def test_is_almost_one(self, field):
        """`value` is within an acceptable threshold of `field.one`."""
        value = 1.0 + utils.WITHIN_THRESHOLD

        assert pytest.approx(field.one, abs=utils.DEFAULT_THRESHOLD) == value
        assert field.is_one(value)

    @pytest.mark.parametrize("field", utils.NON_10_FIELDS)
    def test_is_slightly_not_one(self, field):
        """`value` is not within an acceptable threshold of `field.one`."""
        value = 1.0 + utils.NOT_WITHIN_THRESHOLD

        assert pytest.approx(field.one, abs=utils.DEFAULT_THRESHOLD) != value
        assert not field.is_one(value)

    @pytest.mark.parametrize("field", utils.ALL_FIELDS)
    @pytest.mark.parametrize("value", utils.ZEROS)
    def test_is_not_one(self, field, value):
        """`value` is not equal to `field.one`."""
        assert field.one != value
        assert not field.is_one(value)


@pytest.mark.repeat(utils.N_RANDOM_DRAWS)
class TestDrawRandomFieldElement:
    """Test `Field.random()`."""

    @pytest.mark.parametrize("field", utils.ALL_FIELDS)
    def test_draw_element_with_default_bounds(self, field):
        """Draw a random element from the `field`, ...

        ... within the `field`'s default bounds.

        Here, the default bounds come from the default arguments.
        """
        element = field.random()

        assert field.validate(element)

    @pytest.mark.parametrize("field", utils.ALL_FIELDS)
    def test_draw_element_with_default_bounds_set_to_none(self, field):
        """Draw a random element from the `field`, ...

        ... within the `field`'s default bounds.

        If no default arguments are defined in `field.random()`,
        the internal `Field._get_bounds()` method provides them.
        """
        element = field.random(lower=None, upper=None)

        assert field.validate(element)

    @pytest.mark.parametrize("field", utils.NON_10_FIELDS)
    def test_draw_element_with_custom_bounds(self, field):
        """Draw a random element from the `field` ...

        ... within the bounds passed in as arguments.

        For `GF2`, this only works in non-`strict` mode.
        """
        lower = 200 * random.random() - 100  # noqa: S311
        upper = 200 * random.random() - 100  # noqa: S311

        # `field.random()` sorts the bounds internally
        # => test both directions
        element1 = field.random(lower=lower, upper=upper)
        element2 = field.random(lower=upper, upper=lower)

        assert field.validate(element1)
        assert field.validate(element2)

        # Done implicitly in `field.random()` above
        lower, upper = field.cast(lower), field.cast(upper)

        # Not all data types behind the `Field._cast_func()`
        # support sorting the numbers (e.g., `complex`)
        try:
            swap = upper < lower
        except TypeError:
            pass
        else:
            if swap:
                lower, upper = upper, lower

            assert lower <= element1 <= upper
            assert lower <= element2 <= upper


def test_numbers():
    """We use `0`, `1`, `+42`, and `-42` in different data types."""
    unique_one_and_zero = {int(n) for n in utils.ONES_N_ZEROS}
    unique_non_one_and_zero = {int(n) for n in utils.NON_ONES_N_ZEROS}
    unique_numbers = {int(n) for n in utils.NUMBERS}

    assert unique_one_and_zero == {0, 1}
    assert unique_non_one_and_zero == {+42, -42}
    assert unique_numbers == {0, 1, +42, -42}
