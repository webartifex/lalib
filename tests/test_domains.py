"""Tests for `lalib.domains.Domain`."""

import os
import random

import pytest

from lalib.domains import Domain


CROSS_REFERENCE = not os.environ.get("NO_CROSS_REFERENCE")


NUMERIC_LABELS = (1, 42)  # always interpreted in a canonical way

CANONICAL_ITERABLE_LABELS = tuple(range(number) for number in NUMERIC_LABELS)
NON_CANONICAL_ITERABLE_LABELS = (
    range(1, 42),
    [-42, 0, +42],
    "abc",
    ("x", "y", "z"),
)
ITERABLE_LABELS = CANONICAL_ITERABLE_LABELS + NON_CANONICAL_ITERABLE_LABELS

CANONICAL_MAPPING_LABELS = (
    {0: 123},
    {0: 123, 1: 456},
)
NON_CANONICAL_MAPPING_LABELS = (
    {0: 123, 42: 456},
    {"a": 123, "b": 456},
)
MAPPING_LABELS = CANONICAL_MAPPING_LABELS + NON_CANONICAL_MAPPING_LABELS

CANONICAL_LABELS = (
    *NUMERIC_LABELS,
    *CANONICAL_ITERABLE_LABELS,
    *CANONICAL_MAPPING_LABELS,
)
NON_CANONICAL_LABELS = (
    *NON_CANONICAL_ITERABLE_LABELS,
    *NON_CANONICAL_MAPPING_LABELS,
)

ALL_LABELS = CANONICAL_LABELS + NON_CANONICAL_LABELS


@pytest.fixture
def domain(request):
    """A `Domain` object."""
    return Domain(request.param)


class TestDomainInstantiation:
    """Test `Domain.__new__()` with good inputs."""

    @pytest.mark.parametrize("domain", ALL_LABELS, indirect=True)
    def test_from_domain(self, domain):
        """`Domain` object passed into `Domain()` is simply returned."""
        new_domain = Domain(domain)

        assert new_domain == domain
        assert new_domain is domain

    @pytest.mark.overlapping_test
    @pytest.mark.parametrize("number", NUMERIC_LABELS)
    def test_from_integer(self, number):
        """Positive `int`eger passed into `Domain()` creates canonical `Domain`.

        This is a convenience feature.
        """
        domain = Domain(number)
        expected = set(range(number))

        assert domain == expected

        if CROSS_REFERENCE:
            assert domain.is_canonical

    @pytest.mark.overlapping_test
    @pytest.mark.parametrize("mapping", MAPPING_LABELS)
    def test_from_mapping(self, mapping):
        """Create `Domain` from various mapping objects."""
        domain = Domain(mapping)
        expected = mapping.keys()

        assert domain == expected

    @pytest.mark.overlapping_test
    @pytest.mark.parametrize("iterable", ITERABLE_LABELS)
    def test_from_iterable(self, iterable):
        """Create `Domain` from various iterable objects."""
        domain = Domain(iterable)
        expected = set(iterable)

        assert domain == expected

    @pytest.mark.overlapping_test
    @pytest.mark.parametrize("number", NUMERIC_LABELS)
    def test_from_iterator_yielding_canonical_labels(self, number):
        """`Domain()` can consume iterators: Providing canonical `labels`."""

        def generator_factory():
            """Yield `0`, `1`, ... `number - 1`."""
            yield from range(number)

        generator = generator_factory()
        domain = Domain(generator)
        expected = set(range(number))

        assert domain == expected

        if CROSS_REFERENCE:
            assert domain.is_canonical

    @pytest.mark.overlapping_test
    def test_from_iterator_yielding_non_canonical_labels(self):
        """`Domain()` can consume iterators: Providing non-canonical `labels`."""

        def generator_factory(p_skipped=0.5):
            """Yield `0`, `1`, ..., `100` with missing values."""
            for i in range(100):
                if random.random() > p_skipped:  # noqa: S311
                    yield i

        generator = generator_factory()
        domain = Domain(generator)

        assert domain is not None

        if CROSS_REFERENCE:
            assert not domain.is_canonical

    @pytest.mark.parametrize("domain", CANONICAL_LABELS, indirect=True)
    def test_from_canonical_repr(self, domain):
        """`repr(domain)` is of the form "Domain(integer)"."""
        new_domain = eval(repr(domain))  # noqa: S307

        assert new_domain == domain

    @pytest.mark.parametrize("domain", NON_CANONICAL_LABELS, indirect=True)
    def test_from_non_canonical_repr(self, domain):
        """`repr(domain)` is of the form "Domain({label1, label2, ...})"."""
        new_domain = eval(repr(domain))  # noqa: S307

        assert new_domain == domain


class TestFailedDomainInstantiation:
    """Test `Domain.__new__()` with bad inputs."""

    def test_wrong_type(self):
        """Cannot create `Domain` from non-numeric or non-iterable object."""
        with pytest.raises(TypeError):
            Domain(object())

    @pytest.mark.parametrize("number", [-42, 0, 4.2])
    def test_from_non_positive_integer(self, number):
        """Non-positive `int`egers passed into `Domain()` do not work."""
        with pytest.raises(ValueError, match="positive integer"):
            Domain(number)

    @pytest.mark.overlapping_test
    def test_from_empty_mapping(self):
        """Cannot create `Domain` from empty mapping objects."""
        empty_dict = {}

        with pytest.raises(ValueError, match="at least one label"):
            Domain(empty_dict)

    @pytest.mark.parametrize("iterable_type", [tuple, list, set])
    def test_from_empty_iterable(self, iterable_type):
        """Cannot create `Domain` from empty iterable objects."""
        empty_iterable = iterable_type()

        with pytest.raises(ValueError, match="at least one label"):
            Domain(empty_iterable)

    @pytest.mark.parametrize("iterable_type", [tuple, list])
    def test_from_iterable_with_non_hashable_labels(self, iterable_type):
        """Cannot create `Domain` with non-hashable `labels`."""
        bad_iterable = iterable_type(([1], [2], [3]))

        with pytest.raises(TypeError, match="hashable labels"):
            Domain(bad_iterable)


@pytest.mark.overlapping_test
class TestCanonicalProperty:
    """Test `Domain.is_canonical` property."""

    @pytest.mark.parametrize("domain", CANONICAL_LABELS, indirect=True)
    def test_is_canonical(self, domain):
        """A `domain` with `labels` like `0`, `1`, ..."""
        assert domain.is_canonical is True

    @pytest.mark.parametrize("domain", NON_CANONICAL_LABELS, indirect=True)
    def test_is_not_canonical(self, domain):
        """A `domain` with `labels` unlike `0`, `1`, ..."""
        assert domain.is_canonical is False

    # `@pytest.mark.overlapping_test` can only be used
    # because the one line of code in the `try`-block
    # is always regarded as fully covered,
    # even if an `AttributeError` is raised and excepted
    @pytest.mark.parametrize("domain", ALL_LABELS, indirect=True)
    def test_is_still_canonical_or_not(self, domain):
        """`Domain.is_canonical` is cached."""
        result1 = domain.is_canonical
        result2 = domain.is_canonical

        assert result1 is result2
