"""The concrete `ComplexField`."""

import cmath
import random
from typing import Any

from lalib import config
from lalib.fields import base
from lalib.fields import utils


class ComplexField(utils.SingletonMixin, base.Field):
    """The `Field` over ℂ, the complex numbers."""

    _math_name = "ℂ"
    _dtype = complex
    _post_cast_filter = cmath.isfinite
    _additive_identity = 0 + 0j
    _multiplicative_identity = 1 + 0j

    def random(
        self,
        *,
        lower: complex = _additive_identity,
        upper: complex = _multiplicative_identity,
        ndigits: int = config.NDIGITS,
        **_cast_kwargs: Any,
    ) -> complex:
        """Draw a uniformly distributed random element from the field.

        The `.real` and `.imag`inary parts of the `lower` and `upper`
        bounds evaluated separately; i.e., the `random_element` is drawn
        from a rectangle with opposing corners `lower` and `upper`.

        `lower` and `upper` may come in reversed order.

        Args:
            lower: bound of the random interval
            upper: bound of the random interval
            ndigits: no. of significant digits to the right of the ".";
                both the `.real` and the `.imag`inary parts are rounded

        Returns:
            random_element

        Raises:
            ValueError: `lower` and `upper` are not `.cast()`able
        """
        lower, upper = self._get_bounds(lower, upper)

        random_real, random_imag = (
            # `random.uniform()` can handle `upper < lower`
            round(random.uniform(lower.real, upper.real), ndigits),  # noqa: S311
            round(random.uniform(lower.imag, upper.imag), ndigits),  # noqa: S311
        )

        return complex(random_real, random_imag)

    def is_zero(
        self,
        value: complex,
        /,
        *,
        threshold: float = config.THRESHOLD,
        **_cast_kwargs: Any,
    ) -> bool:
        """Check if `value` equals `0.0 + 0.0j`.

        To be precise: Check if `value` deviates by less than the
        `threshold` from `0.0 + 0.0j` in absolute terms.

        Args:
            value: to be compared to `0.0 + 0.0j`
            threshold: for the equality check

        Returns:
            is_zero

        Raises:
            ValueError: `value` is not `.cast()`able
        """
        return abs(self.cast(value)) < threshold

    def is_one(
        self,
        value: complex,
        /,
        *,
        threshold: float = config.THRESHOLD,
        **_cast_kwargs: Any,
    ) -> bool:
        """Check if `value` equals `1.0 + 0.0j`.

        To be precise: Check if `value` deviates by less than the
        `threshold` from `1.0 + 0.0j` in absolute terms.

        Args:
            value: to be compared to `1.0 + 0.0j`
            threshold: for the equality check

        Returns:
            is_one

        Raises:
            ValueError: `value` is not `.cast()`able
        """
        return abs(self.cast(value) - (1.0 + 0j)) < threshold


C = ComplexField()
