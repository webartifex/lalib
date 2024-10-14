"""Ensure all `Field`s fulfill the axioms from math.

Source: https://en.wikipedia.org/wiki/Field_(mathematics)#Classic_definition
"""

import contextlib
import operator

import pytest

from tests.fields import utils


# None of the test cases below contributes towards higher coverage
pytestmark = pytest.mark.integration_test


@pytest.mark.repeat(utils.N_RANDOM_DRAWS)
@pytest.mark.parametrize("field", utils.ALL_FIELDS)
class TestAllFieldsManyTimes:
    """Run the tests many times for all `field`s."""

    @pytest.mark.parametrize("opr", [operator.add, operator.mul])
    def test_associativity(self, field, opr):
        """`a + (b + c) == (a + b) + c` ...

        ... and `a * (b * c) == (a * b) * c`.
        """
        a, b, c = field.random(), field.random(), field.random()

        left = opr(a, opr(b, c))
        right = opr(opr(a, b), c)

        assert left == pytest.approx(right, abs=utils.DEFAULT_THRESHOLD)

    @pytest.mark.parametrize("opr", [operator.add, operator.mul])
    def test_commutativity(self, field, opr):
        """`a + b == b + a` ...

        ... and `a * b == b * a`.
        """
        a, b = field.random(), field.random()

        left = opr(a, b)
        right = opr(b, a)

        assert left == pytest.approx(right, abs=utils.DEFAULT_THRESHOLD)

    def test_additive_identity(self, field):
        """`a + 0 == a`."""
        a = field.random()

        left = a + field.zero
        right = a

        assert left == pytest.approx(right, abs=utils.DEFAULT_THRESHOLD)

    def test_multiplicative_identity(self, field):
        """`a * 1 == a`."""
        a = field.random()

        left = a * field.one
        right = a

        assert left == pytest.approx(right, abs=utils.DEFAULT_THRESHOLD)

    def test_additive_inverse(self, field):
        """`a + (-a) == 0`."""
        a = field.random()

        left = a + (-a)
        right = field.zero

        assert left == pytest.approx(right, abs=utils.DEFAULT_THRESHOLD)

    def test_multiplicative_inverse(self, field):
        """`a * (1 / a) == 1`."""
        a = field.random()

        # Realistically, `ZeroDivisionError` only occurs for `GF2`
        # => With a high enough `utils.N_RANDOM_DRAWS`
        #    this test case is also `assert`ed for `GF2`
        with contextlib.suppress(ZeroDivisionError):
            left = a * (field.one / a)
            right = field.one

            assert left == pytest.approx(right, abs=utils.DEFAULT_THRESHOLD)

    def test_distributivity(self, field):
        """`a * (b + c) == (a * b) + (a * c)`."""
        a, b, c = field.random(), field.random(), field.random()

        left = a * (b + c)
        right = (a * b) + (a * c)

        assert left == pytest.approx(right, abs=utils.DEFAULT_THRESHOLD)
