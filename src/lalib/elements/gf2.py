"""A Galois field implementation with two elements.

This module defines two singleton objects, `one` and `zero`,
that follow the rules of a Galois field of two elements,
or `GF2` for short:

>>> one + one
zero
>>> zero + one
one
>>> one * one
one
>>> one * zero
zero

They mix with numbers that compare equal to either `1` or `0`,
for example:

>>> one + 1
zero
>>> 0 * zero
zero

Further usage explanations of `one` and `zero`
can be found in the various docstrings of the `GF2` class.
"""

import abc
import functools
import math
import numbers

# When giving up support for Python 3.9, we can get rid of `Optional`
from typing import Callable, ClassVar, Literal, Optional


try:
    from typing import Self
except ImportError:  # pragma: no cover to support Python 3.9 & 3.10
    from typing_extensions import Self


THRESHOLD = 1e-12


def to_gf2(
    value: complex,  # `mypy` reads `complex | float | int`
    *,
    strict: bool = True,
    threshold: float = THRESHOLD,
) -> int:
    """Cast a number as a possible Galois field value: `1` or `0`.

    By default, the `value` is parsed in a `strict` mode where
    `value`s equal to `1` or `0` within the specified `threshold`
    return either `1` or `0` exactly.

    Args:
        value: to be cast; must behave like a number;
            for `complex` numbers their `.real` part is used
        strict: if `True`, only accept `value`s equal to
            `1` or `0` within the `threshold` as `1` or `0`;
            otherwise, cast any number different from `0` as `1`
        threshold: used for the equality checks to find
            `1`-like and `0`-like `value`s

    Returns:
        either `1` or `0`

    Raises:
        TypeError: `value` does not behave like a number
        ValueError: `value != 1` or `value != 0` in `strict` mode
    """
    try:
        value = complex(value)
    except (TypeError, ValueError):
        msg = "`value` must be a number"
        raise TypeError(msg) from None

    if not (abs(value.imag) < threshold):
        msg = "`value` must be either `1`-like or `0`-like"
        raise ValueError(msg)

    value = value.real

    if math.isnan(value):
        msg = "`value` must be either `1`-like or `0`-like"
        raise ValueError(msg)

    if strict:
        if abs(value - 1) < threshold:
            return 1
        if abs(value) < threshold:
            return 0

        msg = "`value` must be either `1`-like or `0`-like"
        raise ValueError(msg)

    if abs(value) < threshold:
        return 0

    return 1


class _GF2Meta(abc.ABCMeta):
    """Make data type of `one` and `zero` appear to be `GF2`."""

    def __repr__(cls) -> str:
        return "GF2"


@functools.total_ordering
class GF2(metaclass=_GF2Meta):
    """A Galois field value: either `one` or `zero`.

    Implements the singleton design pattern such that
    only one instance per field value exists in the
    computer's memory, i.e., there is only one `one`
    and one `zero` object at all times.
    """

    _instances: ClassVar = {}
    _value: int

    @staticmethod
    def __new__(
        cls: type[Self],
        value: object = None,
        *,
        strict: bool = True,
        threshold: float = THRESHOLD,
    ) -> Self:
        """See docstring for `.__init__()`."""
        if isinstance(value, cls):
            return value

        if value is None:
            try:
                value = cls._value
            except AttributeError:
                try:
                    return cls._instances[0]
                except KeyError:
                    msg = "Must create `one` and `zero` first (internal error)"
                    raise RuntimeError(msg) from None
        else:
            value = to_gf2(value, strict=strict, threshold=threshold)  # type: ignore[arg-type]

        try:
            return cls._instances[value]
        except KeyError:
            obj = super().__new__(cls)
            cls._instances[int(obj)] = obj
            return obj

    def __init__(
        self,
        value: object = None,
        *,
        strict: bool = True,
        threshold: float = THRESHOLD,
    ) -> None:
        """Obtain one of two objects: `one` or `zero`.

        Args:
            value: to be cast; must behave like a number;
                for `complex` numbers their `.real` part is used
            strict: if `True`, only accept `value`s equal to
                `1` or `0` within the `threshold` as `one` or `zero`;
                otherwise, cast any number different from `0` as `one`
            threshold: used for the equality checks to find
                `1`-like and `0`-like `value`s

        Returns:
            either `one` or `zero`

        Raises:
            TypeError: `value` does not behave like a number
            ValueError: `value != 1` or `value != 0` in `strict` mode
        """

    def __repr__(self) -> str:
        """Text representation: `repr(one)` and `repr(zero)`.

        `eval(repr(self)) == self` must be `True`; in other words,
        the text representation of an object must be valid code on its
        own and evaluate into a (new) object with the same value.

        See: https://docs.python.org/3/reference/datamodel.html#object.__repr__
        """
        return "one" if self._value else "zero"

    __str__ = __repr__

    def __complex__(self) -> complex:
        """Cast `self` as a `complex` number: `complex(self)`."""
        return complex(self._value, 0)

    def __float__(self) -> float:
        """Cast `self` as a `float`ing-point number: `float(self)`."""
        return float(self._value)

    def __int__(self) -> int:
        """Cast `self` as a `int`: `int(self)`."""
        return int(self._value)

    __hash__ = __int__

    def __bool__(self) -> bool:
        """Cast `self` as a `bool`ean: `bool(self)`.

        Example usage:

        >>> bool(zero)
        False
        >>> if zero + one:
        ...     result = one
        ... else:
        ...     result = zero
        >>> result
        one
        """
        return bool(self._value)

    def __abs__(self) -> Self:
        """Take the absolute value of `self`: `abs(self)`."""
        return self

    def __trunc__(self) -> int:
        """Truncate `self` to the next `int`: `math.trunc(self)`."""
        return int(self)

    def __floor__(self) -> int:
        """Round `self` down to the next `int`: `math.floor(self)`."""
        return int(self)

    def __ceil__(self) -> int:
        """Round `self` up to the next `int`: `math.ceil(self)`."""
        return int(self)

    def __round__(self, ndigits: Optional[int] = 0) -> int:
        """Round `self` to the next `int`: `round(self)`."""
        return int(self)

    @property
    def real(self) -> int:
        """The `.real` part of a `complex` number.

        For a non-`complex` number this is the number itself.
        """
        # Return an `int` to align with `.imag` above
        return int(self._value)

    @property
    def imag(self) -> Literal[0]:
        """The `.imag`inary part of a `complex` number.

        For a non-`complex` number this is always `0`.
        """
        # `numbers.Real` returns an `int` here
        # whereas `numbers.Complex` returns a `float`
        # => must return an `int` to make `mypy` happy
        return 0

    def conjugate(self) -> Self:
        """The conjugate of a `complex` number.

        For a non-`complex` number this is the number itself.
        """
        return self

    @property
    def numerator(self) -> int:
        """Smallest numerator when expressed as a `Rational` number.

        Either `1` or `0`.

        Reasoning:
            - `int(one) == 1` => `GF2(1 / 1) == one`
            - `int(zero) == 0` => `GF2(0 / 1) == zero`

        See also docstring for `.denominator`.
        """
        return int(self)

    @property
    def denominator(self) -> Literal[1]:
        """Smallest denominator when expressed as a `Rational` number.

        Always `1` for `GF2` values.

        See also docstring for `.numerator`.
        """
        return 1

    def __eq__(self, other: object) -> bool:
        """Comparison: `self == other`.

        Example usage:

        >>> zero == one
        False
        >>> one == one
        True
        >>> one != zero
        True
        >>> one == 1
        True
        """
        try:
            other = GF2(other)
        except (TypeError, ValueError):
            return False
        else:
            return self is other  # `one` and `zero` are singletons

    def __lt__(self, other: object) -> bool:
        """Comparison: `self < other`.

        Example usage:

        >>> zero < one
        True
        >>> one < one
        False
        >>> 0 < one
        True
        """
        try:
            other = GF2(other)
        except TypeError:
            return NotImplemented
        except ValueError:
            msg = "`other` must be either `1`-like or `0`-like"
            raise ValueError(msg) from None
        else:
            return int(self) < int(other)

    def __le__(self, other: object) -> bool:
        """Comparison: `self <= other`.

        Example usage:

        >>> zero <= one
        True
        >>> zero <= zero
        True
        >>> one <= zero
        False
        >>> zero <= 1
        True
        """
        # The `numbers.Rational` abstract base class requires both
        # `.__lt__()` and `.__le__()` to be present alongside
        # `.__eq__()` => `@functools.total_ordering` is not enough
        return self == other or self < other

    def _compute(self, other: object, func: Callable) -> Self:
        """Run arithmetic operations using `int`s.

        The `GF2` atithmetic operations can transparently be conducted
        by converting `self` and `other` into `int`s first, and
        then "do the math".

        Besides the generic arithmetic, this method also handles the
        casting of non-`GF2` values and various errors occuring
        along the way.
        """
        try:
            other = GF2(other)
        except TypeError:
            return NotImplemented
        except ValueError:
            msg = "`other` must be a `1`-like or `0`-like value"
            raise ValueError(msg) from None
        else:
            try:
                return self.__class__(func(int(self), int(other)))
            except ZeroDivisionError:
                msg = "division by `0`-like value"
                raise ZeroDivisionError(msg) from None

    def __pos__(self) -> Self:
        """Make `self` positive: `+self`."""
        return self

    def __neg__(self) -> Self:
        """Make `self` negative: `-self`."""
        return self

    def __add__(self, other: object) -> Self:
        """Addition / Subtraction: `self + other` / `self - other`.

        For `GF2`, addition and subtraction are identical. Besides
        `one + one` which cannot result in a "two", all operations
        behave as one would expect from `int`s.

        Example usage:

        >>> one + one
        zero
        >>> one + zero
        one
        >>> zero - one
        one
        >>> zero + 0
        zero
        >>> 1 + one
        zero
        """
        return self._compute(other, lambda s, o: (s + o) % 2)

    __radd__ = __add__
    __sub__ = __add__
    __rsub__ = __add__

    def __mul__(self, other: object) -> Self:
        """Multiplication: `self * other`.

        Multiplying `GF2` values is like multiplying `int`s.

        Example usage:

        >>> one * one
        one
        >>> zero * one
        zero
        >>> 0 * one
        zero
        """
        return self._compute(other, lambda s, o: s * o)

    __rmul__ = __mul__

    def __truediv__(self, other: object) -> Self:
        """Division: `self / other` and `self // other`.

        Dividing `GF2` values is like dividing `int`s.

        Example usage:

        >>> one / one
        one
        >>> zero // one
        zero
        >>> one / zero
        Traceback (most recent call last):
        ...
        ZeroDivisionError: ...
        >>> 1 // one
        one
        """
        return self._compute(other, lambda s, o: s / o)

    __floordiv__ = __truediv__

    def __rtruediv__(self, other: object) -> Self:
        """(Reflected) Division: `other / self` and `other // self`.

        See docstring for `.__truediv__()`.
        """
        return self._compute(other, lambda s, o: o / s)

    __rfloordiv__ = __rtruediv__

    def __mod__(self, other: object) -> Self:
        """Modulo Division: `self % other`.

        Modulo dividing `GF2` values is like modulo dividing `int`s.

        Example usage:

        >>> one % one
        zero
        >>> zero % one
        zero
        >>> one % zero
        Traceback (most recent call last):
        ...
        ZeroDivisionError: ...
        >>> 1 % one
        zero
        """
        return self._compute(other, lambda s, o: s % o)

    def __rmod__(self, other: object) -> Self:
        """(Reflected) Modulo Division: `other % self`.

        See docstring for `.__mod__()`.
        """
        return self._compute(other, lambda s, o: o % s)

    def __pow__(self, other: object, _modulo: Optional[object] = None) -> Self:
        """Exponentiation: `self ** other`.

        Powers of `GF2` values are like powers of `int`s.

        Example usage:

        >>> one ** one
        one
        >>> zero ** one
        zero
        >>> one ** zero
        one
        >>> 1 ** one
        one
        """
        return self._compute(other, lambda s, o: s**o)

    def __rpow__(self, other: object, _modulo: Optional[object] = None) -> Self:
        """(Reflected) Exponentiation: `other ** self`.

        See docstring for `.__pow__()`.
        """
        return self._compute(other, lambda s, o: o**s)


numbers.Rational.register(GF2)


class GF2One(GF2):
    """The Galois field value `one`."""

    _value = 1


class GF2Zero(GF2):
    """The Galois field value `zero`."""

    _value = 0


one = GF2One()
zero = GF2Zero()
