"""The concrete `RationalField`."""

import fractions
import random
from typing import Any

from lalib import config
from lalib.fields import base
from lalib.fields import utils


class RationalField(utils.SingletonMixin, base.Field):
    """The `Field` over ℚ, the rational numbers.

    Although `Q.cast()` accepts `float`s as possible field elements,
    do so only with care as `float`s are inherently imprecise numbers:

    >>> 0.1 + 0.2
    0.30000000000000004

    To mitigate this, `Q.cast()` cuts off the decimals, as configured
    with the `MAX_DENOMINATOR` setting. So, `float`s with just a couple
    of digits return the possibly desired field element. For example:

    >>> Q.cast(0.1)
    Fraction(1, 10)

    Yet, with the hidden `max_denominator` argument, we can easily
    see how `float`s may result in "weird" `Fraction`s.

    >>> Q.cast(0.1, max_denominator=1_000_000_000_000)
    Fraction(1, 10)
    >>> Q.cast(0.1, max_denominator=1_000_000_000_000_000_000)
    Fraction(3602879701896397, 36028797018963968)

    It is recommended to use `str`ings instead:

    >>> Q.cast("0.1")
    Fraction(1, 10)
    >>> Q.cast("1/10")
    Fraction(1, 10)
    """

    _math_name = "ℚ"
    _dtype = fractions.Fraction

    def _cast_func(
        self,
        value: Any,
        /,
        max_denominator: int = config.MAX_DENOMINATOR,
        **_kwargs: Any,
    ) -> fractions.Fraction:
        return fractions.Fraction(value).limit_denominator(max_denominator)

    _additive_identity = fractions.Fraction(0, 1)
    _multiplicative_identity = fractions.Fraction(1, 1)

    def random(
        self,
        *,
        lower: fractions.Fraction = _additive_identity,
        upper: fractions.Fraction = _multiplicative_identity,
        max_denominator: int = config.MAX_DENOMINATOR,
        **_cast_kwargs: Any,
    ) -> fractions.Fraction:
        """Draw a uniformly distributed random element from the field.

        `lower` and `upper` may come in reversed order.

        Args:
            lower: bound of the random interval
            upper: bound of the random interval
            max_denominator: maximum for `random_element.denominator`

        Returns:
            random_element

        Raises:
            ValueError: `lower` and `upper` are not `.cast()`able
        """
        lower, upper = self._get_bounds(lower, upper)

        # `random.uniform()` can handle `upper < lower`
        random_value = random.uniform(float(lower), float(upper))  # noqa: S311

        return self._cast_func(random_value).limit_denominator(max_denominator)


Q = RationalField()
