"""Test the `gf2` singeltons `one` and `zero`."""

import decimal
import fractions
import importlib
import math
import numbers
import operator
import os
import sys

import pytest

from lalib.elements import galois
from tests import utils


gf2, one, zero = (  # official API outside of `lalib.elements.galois`
    galois.gf2,
    galois.one,
    galois.zero,
)

GF2Element, GF2One, GF2Zero = (  # not part of the official API
    galois.GF2Element,
    type(galois.one),  # The `GF2One` and `GF2Zero` sub-classes
    type(galois.zero),  # are deleted in `lalib.elements.galois`
)

del galois


CROSS_REFERENCE = not os.environ.get("NO_CROSS_REFERENCE")


strict_one_like_values = (
    1,
    1.0,
    1.0 + utils.WITHIN_THRESHOLD,
    (1 + 0j),
    (1 + 0j) + complex(0, utils.WITHIN_THRESHOLD),
    (1 + 0j) + complex(utils.WITHIN_THRESHOLD, 0),
    decimal.Decimal("1"),
    fractions.Fraction(1, 1),
    "1",
    "1.0",
    "1+0j",
)

non_strict_one_like_values = (
    0.0 + utils.NOT_WITHIN_THRESHOLD,
    1.0 + utils.NOT_WITHIN_THRESHOLD,
    (1 + 0j) + complex(utils.NOT_WITHIN_THRESHOLD, 0),
    42,
    decimal.Decimal("42"),
    fractions.Fraction(42, 1),
    "42",
    "42.0",
    "42+0j",
    "+inf",
    "-inf",
)

one_like_values = strict_one_like_values + non_strict_one_like_values

zero_like_values = (
    0,
    0.0,
    0.0 + utils.WITHIN_THRESHOLD,
    (0 + 0j),
    (0 + 0j) + complex(0, utils.WITHIN_THRESHOLD),
    (0 + 0j) + complex(utils.WITHIN_THRESHOLD, 0),
    decimal.Decimal("0"),
    fractions.Fraction(0, 1),
    "0",
    "0.0",
    "0+0j",
)


@pytest.mark.overlapping_test
class TestGF2SubClasses:
    """Test the sub-classes behind `one` and `zero`."""

    def test_gf2_is_an_alias(self):
        """The "`gf2` type" is really just `GF2Element`."""
        assert gf2 is GF2Element

    @pytest.mark.parametrize("cls", [GF2One, GF2Zero])
    def test_sub_classes_for_gf2(self, cls):
        """`GF2One` and `GF2Zero` are sub-classes of `gf2`."""
        assert issubclass(cls, gf2)


@pytest.mark.parametrize("cls", [gf2, GF2One, GF2Zero])
class TestGF2Casting:
    """Test the `gf2` class's constructor.

    `gf2(value, ...)` returns either `one` or `zero`.

    The sub-classes behind `one` and `zero` provide the
    same functionality as `gf2` and have the sole purpose
    of providing a unique `help()` message for `one` and `zero`.
    """

    @pytest.mark.parametrize("value", strict_one_like_values)
    def test_cast_ones_strictly(self, cls, value):
        """`gf2(value, strict=True)` returns `one`."""
        result1 = cls(value)  # `strict=True` by default
        assert result1 is one

        result2 = cls(value, strict=True)
        assert result2 is one

    @pytest.mark.parametrize("value", one_like_values)
    def test_cast_ones_not_strictly(self, cls, value):
        """`gf2(value, strict=False)` returns `one`."""
        result = cls(value, strict=False)
        assert result is one

    @pytest.mark.overlapping_test
    @pytest.mark.parametrize("value", non_strict_one_like_values)
    def test_cannot_cast_ones_strictly(self, cls, value):
        """`gf2(value, strict=False)` returns `1`."""
        with pytest.raises(ValueError, match="`1`-like or `0`-like"):
            cls(value)

        with pytest.raises(ValueError, match="`1`-like or `0`-like"):
            cls(value, strict=True)

    @pytest.mark.parametrize("value", zero_like_values)
    def test_cast_zeros(self, cls, value):
        """`gf2(value, strict=...)` returns `zero`."""
        result1 = cls(value)  # `strict=True` by default
        assert result1 is zero

        result2 = cls(value, strict=True)
        assert result2 is zero

        result3 = cls(value, strict=False)
        assert result3 is zero

    @pytest.mark.parametrize(
        "value",
        [
            complex(1, utils.NOT_WITHIN_THRESHOLD),
            complex(0, utils.NOT_WITHIN_THRESHOLD),
        ],
    )
    @pytest.mark.parametrize("strict", [True, False])
    def test_cannot_cast_with_non_zero_imag_part(self, cls, value, strict):
        """Cannot create `one` or `zero` if `.imag != 0`."""
        with pytest.raises(ValueError, match="`1`-like or `0`-like"):
            cls(value, strict=strict)

    @pytest.mark.overlapping_test
    @pytest.mark.parametrize("value", ["abc", (1,), [1]])
    @pytest.mark.parametrize("strict", [True, False])
    def test_cannot_cast_from_wrong_type(self, cls, value, strict):
        """Cannot create `one` or `zero` from a non-numeric value."""
        with pytest.raises(TypeError):
            cls(value, strict=strict)

    @pytest.mark.overlapping_test
    @pytest.mark.parametrize("strict", [True, False])
    def test_cannot_cast_from_nan_value(self, cls, strict):
        """Cannot create `one` or `zero` from undefined value."""
        with pytest.raises(ValueError, match="`1`-like or `0`-like"):
            cls(float("NaN"), strict=strict)

    @pytest.mark.overlapping_test
    @pytest.mark.parametrize("scaler", [1, 10, 100, 1000])
    def test_get_one_if_within_threshold(self, cls, scaler):
        """`gf2()` returns `one` if `value` is larger than `threshold`."""
        # `NOT_WITHIN_THRESHOLD` is larger than the `DEFAULT_THRESHOLD`
        # but still different from `1` => `strict=False`
        value = scaler * utils.NOT_WITHIN_THRESHOLD
        threshold = scaler * utils.DEFAULT_THRESHOLD

        result = cls(value, strict=False, threshold=threshold)
        assert result is one

    @pytest.mark.overlapping_test
    @pytest.mark.parametrize("scaler", [1, 10, 100, 1000])
    @pytest.mark.parametrize("strict", [True, False])
    def test_get_zero_if_within_threshold(self, cls, scaler, strict):
        """`gf2()` returns `zero` if `value` is smaller than `threshold`."""
        # `WITHIN_THRESHOLD` is smaller than the `DEFAULT_THRESHOLD`
        value = scaler * utils.WITHIN_THRESHOLD
        threshold = scaler * utils.DEFAULT_THRESHOLD

        result = cls(value, strict=strict, threshold=threshold)
        assert result is zero


@pytest.mark.overlapping_test
@pytest.mark.parametrize("strict", [True, False])
class TestGF2ConstructorWithoutCastedValue:
    """Test the `gf2` class's constructor.

    `gf2()` returns either `one` or `zero`.
    """

    def test_get_one_from_sub_class_with_no_input_value(self, strict):
        """`GF2One()` returns `one`."""
        result = GF2One(strict=strict)
        assert result is one

    @pytest.mark.parametrize("cls", [gf2, GF2Zero])
    def test_get_zero_with_no_input_value(self, cls, strict):
        """`gf2()` and `GF2Zero()` return `zero`."""
        result = cls(strict=strict)
        assert result is zero


class TestGenericBehavior:
    """Test the classes behind `one` and `zero`."""

    def test_cannot_instantiate_base_class_alone(self, monkeypatch):
        """`GF2One` and `GF2Zero` must be instantiated before `gf2`."""
        monkeypatch.setattr(gf2, "_instances", {})
        with pytest.raises(RuntimeError, match="internal error"):
            gf2()

    @pytest.mark.overlapping_test
    @pytest.mark.parametrize("cls", [gf2, GF2One, GF2Zero])
    def test_create_singletons(self, cls):
        """Singleton pattern: The classes always return the same instance."""
        first = cls()
        second = cls()
        assert first is second

    @pytest.mark.overlapping_test
    @pytest.mark.parametrize("obj", [one, zero])
    def test_sub_classes_return_objs(self, obj):
        """`type(one)` and `type(zero)` return ...

        the sub-classes that create `one` and `zero`.
        """
        sub_cls = type(obj)
        assert sub_cls is not gf2

        new_obj = sub_cls()
        assert new_obj is obj

    @pytest.mark.overlapping_test
    @pytest.mark.parametrize("obj", [one, zero])
    @pytest.mark.parametrize(
        "type_",
        [
            numbers.Number,
            numbers.Complex,
            numbers.Real,
            numbers.Rational,
        ],
    )
    def test_objs_are_numbers(self, obj, type_):
        """`one` and `zero` are officially `Numbers`s."""
        assert isinstance(obj, type_)

    @pytest.mark.overlapping_test
    @pytest.mark.parametrize("cls", [gf2, GF2One, GF2Zero])
    @pytest.mark.parametrize(
        "method",
        [
            "__abs__",
            "__trunc__",
            "__floor__",
            "__ceil__",
            "__round__",
            "__floordiv__",
            "__rfloordiv__",
            "__mod__",
            "__rmod__",
            "__lt__",
            "__le__",
            "numerator",
            "denominator",
        ],
    )
    @pytest.mark.parametrize("value", [1, 0])
    def test_classes_fulfill_rational_numbers_abc(
        self,
        cls,
        method,
        monkeypatch,
        value,
    ):
        """Ensure all of `numbers.Rational`'s abstact methods are implemented."""
        monkeypatch.setattr(gf2, "_instances", {})
        monkeypatch.delattr(gf2, method)

        sub_cls = type("GF2Baby", (cls, numbers.Rational), {})

        with pytest.raises(TypeError, match="instantiate abstract class"):
            sub_cls(value)

    @pytest.mark.parametrize("func", [repr, str])
    @pytest.mark.parametrize("obj", [one, zero])
    def test_text_repr_for_objs(self, func, obj):
        """`repr(one)` and `repr(zero)` return "one" and "zero" ...

        ... which is valid code evaluating into the objects themselves.

        `str()` does the same as `repr()`.
        """
        new_obj = eval(func(obj))  # noqa: S307
        assert new_obj is obj

    @pytest.mark.parametrize("func", [repr, str])
    @pytest.mark.parametrize("obj", [one, zero])
    def test_text_repr_for_classes(self, func, obj):
        """'gf2' is the text representation for all sub-classes ...

        ... which is valid code referring to the base class `gf2`.

        `gf2()` returns `zero` if called without arguments.
        """
        base_cls = eval(func(type(obj)))  # noqa: S307
        assert base_cls is gf2

        new_obj = base_cls()
        assert new_obj is zero


class TestNumericBehavior:
    """Test how `one` and `zero` behave like numbers."""

    @pytest.mark.overlapping_test
    def test_make_complex(self):
        """`one` and `zero` behave like `1 + 0j` and `0 + 0j`."""
        assert (complex(one), complex(zero)) == (1 + 0j, 0 + 0j)

    @pytest.mark.overlapping_test
    def test_make_float(self):
        """`one` and `zero` behave like `1.0` and `0.0`."""
        assert (float(one), float(zero)) == (1.0, 0.0)

    @pytest.mark.overlapping_test
    @pytest.mark.parametrize("func", [int, hash])
    def test_make_int(self, func):
        """`one` and `zero` behave like `1` and `0`.

        That also holds true for their hash values.
        """
        assert (func(one), func(zero)) == (1, 0)

    def test_make_bool(self):
        """`one` and `zero` behave like `True` and `False`."""
        assert (bool(one), bool(zero)) == (True, False)

    @pytest.mark.overlapping_test
    @pytest.mark.parametrize("obj", [one, zero])
    def test_get_abs_value(self, obj):
        """`abs(one)` and `abs(zero)` are `one` and `zero`."""
        assert abs(obj) is obj

    @pytest.mark.parametrize("obj", [one, zero])
    @pytest.mark.parametrize("func", [math.trunc, math.floor, math.ceil, round])
    def test_round_obj(self, obj, func):
        """`func(one)` and `func(zero)` equal `1` and `0`."""
        assert func(obj) in (1, 0)

        if CROSS_REFERENCE:
            assert func(obj) == obj

    def test_real_part(self):
        """`one.real` and `zero.real` are `1` and `0`."""
        assert (one.real, zero.real) == (1, 0)

    def test_imag_part(self):
        """`one.imag` and `zero.imag` are `0`."""
        assert (one.imag, zero.imag) == (0, 0)

    def test_conjugate(self):
        """`one.conjugate()` and `zero.conjugate()` are `1 + 0j` and `0 + 0j`."""
        assert (one.conjugate(), zero.conjugate()) == (1 + 0j, 0 + 0j)

    @pytest.mark.overlapping_test
    def test_one_as_fraction(self):
        """`one.numerator / one.denominator` equals `1`."""
        assert (one.numerator, one.denominator) == (1, 1)

    @pytest.mark.overlapping_test
    def test_zero_as_fraction(self):
        """`one.numerator / one.denominator` equals `0`."""
        assert (zero.numerator, zero.denominator) == (0, 1)


class TestComparison:
    """Test `one` and `zero` interact with relational operators."""

    @pytest.mark.overlapping_test
    @pytest.mark.parametrize("obj", [one, zero])
    def test_equal_to_itself(self, obj):
        """`one` and `zero` are equal to themselves."""
        assert obj == obj  # noqa: PLR0124

    @pytest.mark.overlapping_test
    @pytest.mark.parametrize(
        ["first", "second"],
        [
            (one, one),
            (one, 1),
            (one, 1.0),
            (one, 1 + 0j),
            (zero, zero),
            (zero, 0),
            (zero, 0.0),
            (zero, 0 + 0j),
        ],
    )
    def test_equal_to_another(self, first, second):
        """`one` and `zero` are equal to `1`-like and `0`-like numbers."""
        assert first == second
        assert second == first

    @pytest.mark.overlapping_test
    @pytest.mark.parametrize(
        ["first", "second"],
        [
            (one, zero),
            (one, 0),
            (one, 0.0),
            (one, 0 + 0j),
            (zero, 1),
            (zero, 1.0),
            (zero, 1 + 0j),
        ],
    )
    def test_not_equal_to_another_one_or_zero_like(self, first, second):
        """`one` and `zero` are not equal to `0`-like and `1`-like numbers."""
        assert first != second
        assert second != first

    @pytest.mark.overlapping_test
    @pytest.mark.parametrize(
        ["first", "second"],
        [
            (one, 42),
            (one, 42.0),
            (one, 42 + 0j),
            (one, 0 + 42j),
            (zero, 42),
            (zero, 42.0),
            (zero, 42 + 0j),
            (zero, 0 + 42j),
        ],
    )
    def test_not_equal_to_another_non_one_like(self, first, second):
        """`one` and `zero` are not equal to non-`1`-or-`0`-like numbers."""
        assert first != second
        assert second != first

    @pytest.mark.parametrize("operator", [operator.gt, operator.ge])
    def test_one_greater_than_or_equal_to_zero(self, operator):
        """`one > zero` and `one >= zero`."""
        assert operator(one, zero)

    @pytest.mark.overlapping_test
    @pytest.mark.parametrize("operator", [operator.lt, operator.le])
    def test_one_not_smaller_than_or_equal_to_zero(self, operator):
        """`not one < zero` and `not one <= zero`."""
        assert not operator(one, zero)

    @pytest.mark.overlapping_test
    @pytest.mark.parametrize("operator", [operator.lt, operator.le])
    def test_zero_smaller_than_or_equal_to_one(self, operator):
        """`zero < one` and `zero <= one`."""
        assert operator(zero, one)

    @pytest.mark.overlapping_test
    @pytest.mark.parametrize("operator", [operator.gt, operator.ge])
    def test_zero_not_greater_than_or_equalt_to_one(self, operator):
        """`not zero > one` and `not zero >= one`."""
        assert not operator(zero, one)

    @pytest.mark.overlapping_test
    @pytest.mark.parametrize("obj", [one, zero])
    def test_obj_not_strictly_greater_than_itself(self, obj):
        """`obj >= obj` but not `obj > obj`."""
        assert obj >= obj  # noqa: PLR0124
        assert not obj > obj  # noqa: PLR0124

    @pytest.mark.overlapping_test
    @pytest.mark.parametrize("obj", [one, zero])
    def test_obj_not_strictly_smaller_than_itself(self, obj):
        """`obj <= obj` but not `obj < obj`."""
        assert obj <= obj  # noqa: PLR0124
        assert not obj < obj  # noqa: PLR0124

    @pytest.mark.parametrize("obj", [one, zero])
    @pytest.mark.parametrize(
        "operator",
        [operator.gt, operator.ge, operator.lt, operator.le],
    )
    def test_compare_to_other_operand_of_wrong_type(self, obj, operator):
        """`one` and `zero` may only interact with numbers."""
        with pytest.raises(TypeError):
            operator(obj, "abc")

        with pytest.raises(TypeError):
            operator("abc", obj)

    @pytest.mark.parametrize("obj", [one, zero])
    @pytest.mark.parametrize(
        "operator",
        [operator.gt, operator.ge, operator.lt, operator.le],
    )
    def test_compare_to_other_operand_of_wrong_value(self, obj, operator):
        """`one` and `zero` may only interact with `1`-like or `0`-like numbers."""
        with pytest.raises(ValueError, match="`1`-like or `0`-like"):
            operator(obj, 42)

        with pytest.raises(ValueError, match="`1`-like or `0`-like"):
            operator(42, obj)


class TestArithmetic:
    """Test `one` and `zero` interact with arithmetic operators."""

    @pytest.mark.parametrize("obj", [one, zero])
    @pytest.mark.parametrize("operator", [operator.pos, operator.neg])
    def test_make_obj_positive_or_negative(self, obj, operator):
        """`+one` and `+zero` equal `-one` and `-zero`."""
        assert obj is operator(obj)

    @pytest.mark.parametrize(
        "objs",
        [
            (one, one, zero),
            (one, zero, one),
            (zero, zero, zero),
            (one, 1, zero),
            (one, 1.0, zero),
            (one, 1 + 0j, zero),
            (one, 0, one),
            (one, 0.0, one),
            (one, 0 + 0j, one),
            (zero, 1, one),
            (zero, 1.0, one),
            (zero, 1 + 0j, one),
            (zero, 0, zero),
            (zero, 0.0, zero),
            (zero, 0 + 0j, zero),
        ],
    )
    @pytest.mark.parametrize("operator", [operator.add, operator.sub])
    def test_addition_and_subtraction(self, objs, operator):
        """Adding and subtracting `one` and `zero` is identical and commutative."""
        first, second, expected = objs

        result1 = operator(first, second)
        assert result1 is expected

        result2 = operator(second, first)
        assert result2 is expected

        if CROSS_REFERENCE:  # cast `one` and `zero` as `integer`s before doing the math

            result3 = gf2((operator(int(abs(first)), int(abs(second))) + 2) % 2)
            assert result3 is expected

            result4 = gf2((operator(int(abs(second)), int(abs(first))) + 2) % 2)
            assert result4 is expected

    @pytest.mark.parametrize(
        ["first", "second", "expected"],
        [
            (one, one, one),
            (one, zero, zero),
            (zero, zero, zero),
            (one, 1, one),
            (one, 1.0, one),
            (one, 1 + 0j, one),
            (one, 0, zero),
            (one, 0.0, zero),
            (one, 0 + 0j, zero),
            (zero, 1, zero),
            (zero, 1.0, zero),
            (zero, 1 + 0j, zero),
            (zero, 0, zero),
            (zero, 0.0, zero),
            (zero, 0 + 0j, zero),
        ],
    )
    def test_multiplication(self, first, second, expected):
        """Multiplying `one` and `zero` is commutative."""
        result1 = first * second
        assert result1 is expected

        result2 = second * first
        assert result2 is expected

        if CROSS_REFERENCE:  # cast `one` and `zero` as `integer`s before doing the math

            result3 = gf2(int(abs(first)) * int(abs(second)))
            assert result3 is expected

            result4 = gf2(int(abs(second)) * int(abs(first)))
            assert result4 is expected

    @pytest.mark.overlapping_test
    @pytest.mark.parametrize(
        "objs",
        [
            # In Python 3.9 we cannot floor-divide a `complex` number
            (one, one, one),
            (one, 1, one),
            (one, 1.0, one),
            (one, 1 + 0j, one),
            (1, one, one),
            (1.0, one, one),
            (zero, one, zero),
            (zero, 1, zero),
            (zero, 1.0, zero),
            (zero, 1 + 0j, zero),
            (0, one, zero),
            (0.0, one, zero),
        ],
    )
    @pytest.mark.parametrize(
        "operator",
        [operator.truediv, operator.floordiv],
    )
    def test_division_by_one(self, objs, operator):
        """Division by `one`."""
        first, second, expected = objs

        result1 = operator(first, second)
        assert result1 is expected

        if CROSS_REFERENCE:  # cast `one` and `zero` as `integer`s before doing the math

            result2 = gf2(operator(int(abs(first)), int(abs(second))))
            assert result2 is expected

    @pytest.mark.overlapping_test
    @pytest.mark.parametrize(
        "objs",
        [
            # In Python 3.9 we cannot modulo-divide a `complex` number
            (one, one, zero),
            (one, 1, zero),
            (one, 1.0, zero),
            (one, 1 + 0j, zero),
            (1, one, zero),
            (1.0, one, zero),
            (zero, one, zero),
            (zero, 1, zero),
            (zero, 1.0, zero),
            (zero, 1 + 0j, zero),
            (0, one, zero),
            (0.0, one, zero),
        ],
    )
    def test_modulo_division_by_one(self, objs):
        """Division by `one`."""
        first, second, expected = objs

        result1 = first % second
        assert result1 is expected

        if CROSS_REFERENCE:  # cast `one` and `zero` as `integer`s before doing the math

            result2 = gf2(int(abs(first)) % int(abs(second)))
            assert result2 is expected

    @pytest.mark.parametrize(
        "objs",
        [
            # In Python 3.9 we cannot floor-divide a `complex` number
            (one, zero),
            (one, 0),
            (one, 0.0),
            (1, zero),
            (1.0, zero),
            (zero, zero),
            (zero, 0),
            (zero, 0.0),
            (0, zero),
            (0.0, zero),
        ],
    )
    @pytest.mark.parametrize(
        "operator",
        [operator.truediv, operator.floordiv, operator.mod],
    )
    def test_division_by_zero(self, objs, operator):
        """Division by `zero` raises `ZeroDivisionError`."""
        first, second = objs

        with pytest.raises(ZeroDivisionError):
            operator(first, second)

        if CROSS_REFERENCE:  # cast `one` and `zero` as `integer`s before doing the math

            with pytest.raises(ZeroDivisionError):
                operator(int(abs(first)), int(abs(second)))

    @pytest.mark.parametrize(
        "objs",
        [
            (one, one, one),
            (one, 1, one),
            (one, 1.0, one),
            (one, 1 + 0j, one),
            (1, one, one),
            (1.0, one, one),
            (1 + 0j, one, one),
            (zero, one, zero),
            (zero, 1, zero),
            (zero, 1.0, zero),
            (zero, 1 + 0j, zero),
            (0, one, zero),
            (0.0, one, zero),
            (0 + 0j, one, zero),
            (one, zero, one),
            (one, 0, one),
            (one, 0.0, one),
            (one, 0 + 0j, one),
            (1, zero, one),
            (1.0, zero, one),
            (1 + 0j, zero, one),
            (zero, zero, one),
            (zero, 0, one),
            (zero, 0.0, one),
            (zero, 0 + 0j, one),
            (0, zero, one),
            (0.0, zero, one),
            (0 + 0j, zero, one),
        ],
    )
    def test_to_the_power_of(self, objs):
        """Exponentiation with `one` and `zero`."""
        first, second, expected = objs

        result1 = first**second
        assert result1 is expected

        if CROSS_REFERENCE:  # cast `one` and `zero` as `integer`s before doing the math

            result2 = gf2(int(abs(first)) ** int(abs(second)))
            assert result2 is expected

    @pytest.mark.parametrize("obj", [one, zero])
    @pytest.mark.parametrize(
        "operator",
        [
            operator.add,
            operator.mul,
            operator.truediv,
            operator.floordiv,
            operator.mod,
            operator.pow,
        ],
    )
    def test_other_operand_of_wrong_type(self, obj, operator):
        """`one` and `zero` may only interact with numbers."""
        # Cannot use a `str` like `"abc"` as then `%` means string formatting
        with pytest.raises(TypeError):
            operator(obj, ("a", "b", "c"))

        with pytest.raises(TypeError):
            operator(("a", "b", "c"), obj)

    @pytest.mark.parametrize("obj", [one, zero])
    @pytest.mark.parametrize(
        "operator",
        [
            operator.add,
            operator.mul,
            operator.truediv,
            operator.floordiv,
            operator.mod,
            operator.pow,
        ],
    )
    def test_other_operand_of_wrong_value(self, obj, operator):
        """`one` and `zero` may only interact with `1`-like or `0`-like numbers."""
        with pytest.raises(ValueError, match="`1`-like or `0`-like"):
            operator(obj, 42)

        with pytest.raises(ValueError, match="`1`-like or `0`-like"):
            operator(42, obj)


@pytest.mark.overlapping_test
@pytest.mark.skipif(
    not sys.version_info < (3, 11),
    reason='"typing-extensions" are installed to support Python 3.9 & 3.10',
)
def test_can_import_typing_extensions():
    """For Python versions 3.11+ we do not need the "typing-extensions"."""
    package = importlib.import_module("lalib.elements.galois")
    importlib.reload(package)

    assert package.Self is not None


@pytest.mark.sanity_test
def test_thresholds():
    """Sanity check for the thresholds used in the tests below."""
    assert utils.WITHIN_THRESHOLD < utils.DEFAULT_THRESHOLD < utils.NOT_WITHIN_THRESHOLD
