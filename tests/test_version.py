"""Test the package's version identifier.

The packaged version identifier must adhere to PEP440
and a strict subset of semantic versioning:
    - in general, version identifiers must follow the "x.y.z" format
      where x, y, and z are non-negative integers (e.g., "0.1.0" or "1.2.3")
    - non-release and post-release versions are only allowed with
      ".devN" or ".postN" suffixes where N is also a non-negative integer
      (e.g., "1.2.3.dev0" or "0.1.0.post0")
"""

import re

import pytest
from packaging import version as pkg_version

import lalib


class TestPEP404Compliance:
    """Packaged version identifier is PEP440 compliant."""

    @pytest.fixture
    def parsed_version(self):
        """The packaged version."""
        return pkg_version.Version(lalib.__version__)  # noqa:WPS0609

    def test_parsed_version_has_no_epoch(self, parsed_version):
        """PEP440 compliant subset of semantic versioning: no epoch."""
        assert parsed_version.epoch == 0

    def test_parsed_version_is_non_local(self, parsed_version):
        """PEP440 compliant subset of semantic versioning: no local version."""
        assert parsed_version.local is None

    def test_parsed_version_is_no_post_release(self, parsed_version):
        """PEP440 compliant subset of semantic versioning: no post releases."""
        assert parsed_version.is_postrelease is False

    def test_parsed_version_is_all_public(self, parsed_version):
        """PEP440 compliant subset of semantic versioning: all public parts."""
        assert parsed_version.public == lalib.__version__  # noqa:WPS0609


class TestSemanticVersioning:
    """Packaged version follows a strict subset of semantic versioning."""

    version_pattern = re.compile(
        r'^(0|([1-9]\d*))\.(0|([1-9]\d*))\.(0|([1-9]\d*))'  # "x.y.z"
        + r'(\.((dev)|(post))(0|([1-9]\d*)))?$',  # ".devN" or ".postN"
    )

    def test_version_is_semantic(self):
        """Packaged version follows semantic versioning."""
        result = self.version_pattern.fullmatch(lalib.__version__)  # noqa:WPS0609

        assert result is not None

    # The next two test cases are sanity checks to validate the `version_pattern`.

    @pytest.mark.parametrize(
        'version',
        [
            '0.1.0',
            '1.0.0',
            '1.2.3',
            '1.23.456',
            '123.4.56',
            '10.11.12',
            '1.2.3.dev0',
            '1.2.3.dev1',
            '1.2.3.dev10',
            '0.1.0.post0',
            '0.1.0.post1',
            '0.1.0.post10',
        ],
    )
    def test_valid_semantic_versioning(self, version):
        """Versions follow the "x.y.z", "x.y.z.devN", or "x.y.z.postN" formats."""
        result = self.version_pattern.fullmatch(version)

        assert result is not None

    @pytest.mark.parametrize(
        'version',
        [
            '1',
            '1.2',
            '-1.2.3',
            '01.2.3',
            '1.02.3',
            '1.2.03',
            '1.2.3.4',
            '1.2.3.abc',
            '1.2.3-dev0',
            '1.2.3+dev0',
            '1.2.3.d0',
            '1.2.3.develop0',
            '1.2.3.dev-1',
            '1.2.3.dev01',
            '1.2.3..dev0',
            '0.1.0-post0',
            '0.1.0+post0',
            '1-2-3',
            '1,2,3',
            '1..2.3',
            '1.2..3',
        ],
    )
    def test_invalid_semantic_versioning(self, version):
        """Versions follow the "x.y.z", "x.y.z.devN", or "x.y.z.postN" formats."""
        result = self.version_pattern.fullmatch(version)

        assert result is None
