"""A `Domain` for discrete `Vector`s.

This module defines a `Domain` class wrapping the built-in `frozenset`.
It is designed to model domains of discrete vectors and matrices.

In conventional math, `Domain`s are implicitly thought of as strictly
positive natural numbers. For example, a `3`-vector over the reals
would then have a `Domain` like below:

>>> Domain([1, 2, 3])
Domain({1, 2, 3})

However, in Python we commonly start counting at `0`. Therefore,
a `3`-vector over the reals has the following `Domain` in `lalib`:

>>> Domain([0, 1, 2])
Domain(3)

We call such `Domain`s "canonical", and, as a convenience, such
`Domain`s can be created by passing a `Vector`'s "length" as an
`int`eger argument to the `Domain()` constructor, for example:

>>> Domain(5)
Domain(5)

Domains do not need to be made of numbers. Instead, we can use,
for example, letters or words, or any other `hash`able object.

>>> Domain(["a", "b", "c"])
...

>>> Domain("abc")
...

>>> Domain(("heads", "tails"))
...

>>> Domain({(1, 23), (4, 56), (7, 89)})
...

>>> Domain({"n_yes": 7, "n_no": 3, "n_total": 10})  # `.keys()` are used
...

>>> Domain(([1, 23], [4, 56], [7, 89]))
Traceback (most recent call last):
...
TypeError: ...
"""

from collections import abc as collections_abc

# When giving up support for Python 3.9, we can get rid of `Union`
from typing import Union


try:
    from typing import Self
except ImportError:  # pragma: no cover to support Python 3.9 & 3.10
    from typing_extensions import Self


class Domain(frozenset):
    """The domain for a `Vector`."""

    @staticmethod
    def __new__(
        cls: type[Self],
        /,
        labels: Union[collections_abc.Iterable[collections_abc.Hashable], int],
    ) -> Self:
        """See docstring for `.__init__()`."""
        # Because `Domain` objects are immutable by design ...
        if isinstance(labels, cls):
            return labels

        if not isinstance(labels, collections_abc.Iterable):
            try:
                n_labels = int(labels)
            except (TypeError, ValueError):
                msg = "must provide a positive integer"
                raise TypeError(msg) from None
            else:
                if n_labels != labels:
                    msg = "must provide a positive integer"
                    raise ValueError(msg)

            labels = range(n_labels)

        # As we require `Vector`s to have at least one entry,
        if not labels:  # we also enforce this constraint on the `Domain`s
            msg = "must provide at least one label or a positive integer"
            raise ValueError(msg)

        try:
            return super().__new__(cls, labels)
        except TypeError:
            # Provide a nicer error message
            msg = "must provide hashable labels"
            raise TypeError(msg) from None

    def __init__(
        self,
        /,
        labels: Union[collections_abc.Iterable[collections_abc.Hashable], int],
    ) -> None:
        """Create a new domain.

        Args:
            labels: the domain labels provided by an iterable or
                a strictly positive `int`eger `n` that then constructs
                the labels `0`, `1`, ... up to and including `n - 1`

        Returns:
            domain

        Raises:
            TypeError: `labels` is not of the specified types
            ValueError:
                - if a collection argument contains no elements
                - if an integer argument is not strictly positive
        """

    def __repr__(self) -> str:
        """Text representation: `Domain(...)`.

        Designed such that `eval(repr(self)) == self`; in other words,
        the text representation of a `Domain` is valid code on its own
        evaluating into a (new) `Domain` with the same `labels`.

        See: https://docs.python.org/3/reference/datamodel.html#object.__repr__
        """
        if self.is_canonical:
            return f"{self.__class__.__name__}({len(self)})"
        return super().__repr__()

    @property  # We do not use `@functools.cached_property`
    #            as this allows writing to the propery
    def is_canonical(self) -> bool:
        """If the `labels` resemble a `range(...)`."""
        try:
            cached = self._is_canonical
        except AttributeError:
            self._is_canonical: bool = (cached := self == set(range(len(self))))
        return cached
