"""The concrete `GaloisField2`."""

import random
from typing import Any

from lalib import config
from lalib.elements import galois as gf2_elements
from lalib.fields import base
from lalib.fields import utils


class GaloisField2(utils.SingletonMixin, base.Field):
    """The Galois `Field` of 2 elements."""

    _math_name = "GF2"
    _dtype = gf2_elements.GF2Element

    def _cast_func(
        self,
        value: Any,
        /,
        *,
        strict: bool = True,
        threshold: float = config.THRESHOLD,
        **_kwargs: Any,
    ) -> gf2_elements.GF2Element:
        return gf2_elements.gf2(value, strict=strict, threshold=threshold)

    _additive_identity = gf2_elements.zero
    _multiplicative_identity = gf2_elements.one

    def random(
        self,
        lower: gf2_elements.GF2Element = gf2_elements.zero,
        upper: gf2_elements.GF2Element = gf2_elements.one,
        **cast_kwargs: Any,
    ) -> gf2_elements.GF2Element:
        """Draw a uniformly distributed random element from the field.

        Args:
            lower: bound of the random interval
            upper: bound of the random interval
            **cast_kwargs: extra `kwargs` to `.cast()`
                the `lower` and `upper` bounds

        Returns:
            random_element: either `one` or `zero`

        Raises:
            ValueError: `lower` and `upper` are not `.cast()`able
        """
        lower, upper = self._get_bounds(lower, upper, **cast_kwargs)

        # `random.choice()` can handle `upper < lower`
        return random.choice((lower, upper))  # noqa: S311


GF2 = GaloisField2()
