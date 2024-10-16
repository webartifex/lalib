"""The abstract blueprint of a `Field`."""

import abc
import numbers
from typing import Any, Callable, Generic, TypeVar


T = TypeVar("T", bound=numbers.Real)


class Field(abc.ABC, Generic[T]):
    """The abstract blueprint of a mathematical field."""

    @property
    @abc.abstractmethod
    def _math_name(self) -> str:
        """The common abbreviation used in math notation."""

    @staticmethod
    @abc.abstractmethod
    def _dtype(value: Any, /) -> T:
        """Data type to store the `Field` elements."""

    def _cast_func(self, value: Any, /, **kwargs: Any) -> T:
        """Function to cast `value`s as field elements."""
        return self._dtype(value, **kwargs)

    @staticmethod
    def _post_cast_filter(possible_element: T, /) -> bool:  # noqa: ARG004
        """Function to filter out castable `value`s.

        Called after a successfull call of the `._cast_func()`.

        For example, if one wants to avoid non-finite `Field` elements,
        an overwriting `._post_cast_filter()` could return `False` for
        non-finite `value`s like `float("NaN")`.

        By default, all castable `value`s may become `Field` elements.
        """
        return True

    @property
    @abc.abstractmethod
    def _additive_identity(self) -> T:
        """The field's additive identity."""

    @property
    @abc.abstractmethod
    def _multiplicative_identity(self) -> T:
        """The field's multiplicative identity."""

    def cast(
        self,
        value: object,
        /,
        **cast_kwargs: Any,
    ) -> T:
        """Cast a (numeric) `value` as an element of the field.

        Args:
            value: to be cast as the "right" data type
                as defined in the concrete `Field` sub-class
            **cast_kwargs: extra `kwargs` to the `._cast_func()`

        Returns:
            element: of the concrete `Field`

        Raises:
            ValueError: `value` is not an element of the field
        """
        try:
            element = self._cast_func(value, **cast_kwargs)  # type: ignore[arg-type]
        except (ArithmeticError, TypeError, ValueError):
            msg = "`value` is not an element of the field"
            raise ValueError(msg) from None

        if not self._post_cast_filter(element):
            msg = "`value` is not an element of the field"
            raise ValueError(msg)

        return element

    def validate(
        self,
        value: object,
        /,
        *,
        silent: bool = True,
        **cast_kwargs: Any,
    ) -> bool:
        """Check if a (numeric) `value` is an element of the `Field`.

        Wraps `.cast()`, catches the documented `ValueError`,
        and returns a `bool`ean indicating field membership.

        Args:
            value: see docstring for `.cast()`
            silent: suppress the `ValueError`
            **cast_kwargs: extra `kwargs` to `.cast()` the `value`

        Returns:
            is_element

        Raises:
            ValueError: `value` is not `.cast()`able
                (suppressed by default)
        """
        try:
            self.cast(value, **cast_kwargs)
        except ValueError:
            if not silent:
                raise
            return False

        return True

    @property
    def dtype(self) -> Callable[[Any], T]:
        """Data type to store the `Field` elements."""
        return self._dtype

    @property
    def zero(self) -> T:
        """The field's additive identity."""
        return self._additive_identity

    def is_zero(self, value: T, /, **cast_kwargs: Any) -> bool:
        """Check if `value` equals the `.zero`-like field element.

        This method, together with `.is_one()` below, provides a unified
        way across the different `Field`s to check if a given `value`
        equals the field's additive or multiplicative identity.

        Concrete `Field`s may use a different logic. For example, some
        compare the absolute difference between the `value` and the
        `.zero`-or-`.one`-like field element to a small `threshold`.

        Overwriting methods should
        - check the `value` for field membership first, and
        - accept arbitrary keyword-only arguments
          that they may simply ignore

        Args:
            value: see docstring for `.cast()`
            **cast_kwargs: extra `kwargs` to `.cast()` the `value`

        Returns:
            is_zero

        Raises:
            ValueError: `value` is not `.cast()`able
        """
        return self.cast(value, **cast_kwargs) == self._additive_identity

    @property
    def one(self) -> T:
        """The field's multiplicative identity."""
        return self._multiplicative_identity

    def is_one(self, value: T, /, **cast_kwargs: Any) -> bool:
        """Check if `value` equals the `.one`-like field element.

        See docstring for `.is_zero()` above for more details.

        Args:
            value: see docstring for `.cast()`
            **cast_kwargs: extra `kwargs` to `.cast()` the `value`

        Returns:
            is_one

        Raises:
            ValueError: `value` is not `.cast()`able
        """
        return self.cast(value, **cast_kwargs) == self._multiplicative_identity

    @abc.abstractmethod
    def random(
        self,
        *,
        lower: T,
        upper: T,
        **cast_kwargs: Any,
    ) -> T:
        """Draw a uniformly distributed random element from the field.

        `lower` and `upper` may come in reversed order.
        Overwriting methods should sort them if necessary.

        Extra keyword arguments should be passed through to `.cast()`.
        """

    def _get_bounds(
        self,
        lower: T,
        upper: T,
        /,
        **cast_kwargs: Any,
    ) -> tuple[T, T]:
        """Get the `lower` & `upper` bounds for `Field.random()`.

        Utility method to either
         - resolve the given `lower` and `upper` bounds into a
           `.cast()`ed element of the `Field`, or
         - obtain their default `value`s, which are
           + the `.additive_identity` for `lower`, and
           + the `.multiplicative_identity` for `upper`

        Extra keyword arguments are passed through to `.cast()`.
        """
        lower = lower if lower is not None else self._additive_identity
        upper = upper if upper is not None else self._multiplicative_identity

        return (self.cast(lower, **cast_kwargs), self.cast(upper, **cast_kwargs))

    def __repr__(self) -> str:
        """Text representations: `repr(...)` and `str(...)`.

        The `.math_name` should be a valid name within `lalib`.
        If not, use the "<cls ...>" convention; in other words,
        the text representation is no valid code on its own.

        See: https://docs.python.org/3/reference/datamodel.html#object.__repr__
        """
        return self._math_name

    __str__ = __repr__
