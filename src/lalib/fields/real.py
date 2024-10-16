"""The concrete `RealField`."""

import math
import random
from typing import Any

from lalib import config
from lalib.fields import base
from lalib.fields import utils


class RealField(utils.SingletonMixin, base.Field):
    """The `Field` over ℝ, the real numbers."""

    _math_name = "ℝ"
    _dtype = float
    _post_cast_filter = math.isfinite
    _additive_identity = 0.0
    _multiplicative_identity = 1.0

    def random(
        self,
        *,
        lower: float = _additive_identity,
        upper: float = _multiplicative_identity,
        ndigits: int = config.NDIGITS,
        **_cast_kwargs: Any,
    ) -> float:
        """Draw a uniformly distributed random element from the field.

        `lower` and `upper` may come in reversed order.

        Args:
            lower: bound of the random interval
            upper: bound of the random interval
            ndigits: no. of significant digits to the right of the "."

        Returns:
            random_element

        Raises:
            ValueError: `lower` and `upper` are not `.cast()`able
        """
        lower, upper = self._get_bounds(lower, upper)

        # `random.uniform()` can handle `upper < lower`
        lower, upper = float(lower), float(upper)
        rand_value = random.uniform(lower, upper)  # noqa: S311

        return round(rand_value, ndigits)

    def is_zero(
        self,
        value: float,
        /,
        *,
        threshold: float = config.THRESHOLD,
        **_cast_kwargs: Any,
    ) -> bool:
        """Check if `value` equals `0.0`.

        Args:
            value: to be compared to `0.0`
            threshold: for the equality check

        Returns:
            is_zero (boolean)

        Raises:
            ValueError: `value` is not `.cast()`able
        """
        return abs(self.cast(value)) < threshold

    def is_one(
        self,
        value: float,
        /,
        *,
        threshold: float = config.THRESHOLD,
        **_cast_kwargs: Any,
    ) -> bool:
        """Check if `value` equals `1.0`.

        Args:
            value: to be compared to `1.0`
            threshold: for the equality check

        Returns:
            is_one

        Raises:
            ValueError: `value` is not `.cast()`able
        """
        return abs(self.cast(value) - 1.0) < threshold


R = RealField()
