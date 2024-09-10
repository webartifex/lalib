"""Test the package's version identifier.

The packaged version identifier (i.e., `lalib.__version__`)
adheres to PEP440 and its base part follows semantic versioning:

    - In general, version identifiers follow the "x.y.z" format
      where x, y, and z are non-negative integers (e.g., "0.1.0"
      or "1.2.3") matching the "major", "minor", and "patch" parts
      of semantic versioning

    - Without suffixes, these "x.y.z" versions represent
      the ordinary releases to PyPI

    - Developmental or non-release versions are indicated
      with a ".dev0" suffix; we use solely a "0" to keep things simple

    - Pre-releases come as "alpha", "beta", and "release candidate"
      versions, indicated with "aN", "bN", and "rcN" suffixes
      (no "." separator before the suffixes) where N is either 1 or 2

    - Post-releases are possible and indicated with a ".postN" suffix
      where N is between 0 and 9; they must not change the code
      as compared to their corresponding ordinary release version

Examples:
    - "0.4.2" => ordinary release; public API may be unstable
                 as explained by the rules of semantic versioning
    - "1.2.3" => ordinary release (long-term stable versions)
    - "4.5.6.dev0" => early development stage before release "4.5.6"
    - "4.5.6a1" => pre-release shortly before publication of "4.5.6"

Sources:
    - https://peps.python.org/pep-0440/
    - https://semver.org/spec/v2.0.0.html

Implementation notes:

    - The `packaging` library and the `importlib.metadata` module
      are very forgiving when parsing version identifiers
      => The test cases in this file enforce a strict style

    - The `DECLARED_VERSION` (in pyproject.toml) and the
      `PACKAGED_VERSION` (read from the metadata after installation
      in a virtual environment) are tested besides a lot of
      example `VALID_VERSIONS` to obtain a high confidence
      in the test cases

    - There are two generic kind of test cases:

        + `TestVersionIdentifier` uses the `packaging` and `semver
           libraries to parse the various `*_VERSION`s and validate
           their infos

        + `TestVersionIdentifierWithPattern` defines a `regex` pattern
          comprising all rules at once
"""

import contextlib
import importlib
import itertools
import pathlib
import re
import string
import sys

import pytest
import semver
from packaging import version as pkg_version

import lalib


# Support Python 3.9 and 3.10
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]


def load_version_from_pyproject_toml():
    """The version declared in pyproject.toml."""
    with pathlib.Path("pyproject.toml").open("rb") as fp:
        pyproject_toml = tomllib.load(fp)

    return pyproject_toml["tool"]["poetry"]["version"]


def expand_digits_to_versions(
    digits=string.digits[1:],
    *,
    pre_process=(lambda x, y, z: (x, y, z)),
    filter_=(lambda _x, _y, _z: True),
    post_process=(lambda x, y, z: (x, y, z)),
    unique=False,
):
    """Yield examplatory semantic versions.

    For example, "12345" is expanded into "1.2.345", "1.23.45", ..., "123.4.5".

    In general, the `digits` are sliced into three parts `x`, `y`, and `z`
    that could be thought of the "major", "minor", and "patch" parts of
    a version identifier. The `digits` themselves are not re-arranged.

    `pre_process(x, y, z)` transform the parts individually. As an example,
    `part % 100` makes each part only use the least significant digits.
    So, in the example, "1.2.345" becomes "1.2.45".

    `post_process(x, y, z)` does the same but only after applying the
    `filter_(x, y, z)` which signals if the current `x`, `y`, and `z`
    should be skipped.

    `unique=True` ensures a produced version identifier is yielded only once.
    """
    seen_before = set() if unique else None

    for i in range(1, len(digits) - 1):
        for j in range(i + 1, len(digits)):
            x, y, z = int(digits[:i]), int(digits[i:j]), int(digits[j:])

            x, y, z = pre_process(x, y, z)

            if not filter_(x, y, z):
                continue

            x, y, z = post_process(x, y, z)

            if unique:
                if (x, y, z) in seen_before:
                    continue
                else:
                    seen_before.add((x, y, z))

            yield f"{x}.{y}.{z}"


DECLARED_VERSION = load_version_from_pyproject_toml()
PACKAGED_VERSION = lalib.__version__

VALID_AND_NORMALIZED_VERSIONS = (
    "0.1.0",
    "0.1.1",
    "0.1.99",
    "0.2.0",
    "0.99.0",
    "1.0.0",
    "1.2.3.dev0",
    "1.2.3a1",
    "1.2.3a2",
    "1.2.3b1",
    "1.2.3b2",
    "1.2.3rc1",
    "1.2.3rc2",
    "1.2.3",
    *(f"1.2.3.post{n}" for n in range(10)),
    # e.g., "1.2.89", "1.23.89", "1.78.9", "12.3.89", "12.34.89", and "67.8.9"
    *expand_digits_to_versions(
        "12345689",
        pre_process=(lambda x, y, z: (x % 100, y % 100, z % 100)),
    ),
)

# The `packaging` library can parse the following versions
# that are then normalized according to PEP440
# Source: https://peps.python.org/pep-0440/#normalization
VALID_AND_NOT_NORMALIZED_VERSIONS = (
    "1.2.3dev0",
    "1.2.3-dev0",
    "1.2.3_dev0",
    "1.2.3alpha1",
    "1.2.3.alpha1",
    "1.2.3-alpha1",
    "1.2.3_alpha1",
    "1.2.3.a1",
    "1.2.3.a2",
    "1.2.3beta1",
    "1.2.3.beta1",
    "1.2.3-beta1",
    "1.2.3_beta1",
    "1.2.3.b1",
    "1.2.3.b2",
    "1.2.3c1",
    "1.2.3.c1",
    "1.2.3.rc1",
    "1.2.3c2",
    "1.2.3.c2",
    "1.2.3.rc2",
    "1.2.3post0",
    "1.2.3-post0",
    "1.2.3_post0",
    "1.2.3-r0",
    "1.2.3-rev0",
    "1.2.3-0",
    "1.2.3_post9",
)

VALID_VERSIONS = (
    DECLARED_VERSION,
    PACKAGED_VERSION,
    *VALID_AND_NORMALIZED_VERSIONS,
    *VALID_AND_NOT_NORMALIZED_VERSIONS,
)

# The following persions cannot be parsed by the `packaging` library
INVALID_NOT_READABLE = (
    "-1.2.3",
    "+1.2.3",
    "!1.2.3",
    "x.2.3",
    "1.y.3",
    "1.2.z",
    "x.y.z",
    "1.2.3.abc",
    "1.2.3.d0",
    "1.2.3.develop0",
    "1.2.3..dev0",
    "1..2.3",
    "1.2..3",
    "1-2-3",
    "1,2,3",
)

# The `packaging` library is able to parse the following versions
# that however are not considered valid for this project
INVALID_NOT_SEMANTIC = (
    "1",
    "1.2",
    "01.2.3",
    "1.02.3",
    "1.2.03",
    "1.2.3.4",
    "1.2.3.dev-1",
    "1.2.3.dev01",
    "v1.2.3",
)

INVALID_VERSIONS = INVALID_NOT_READABLE + INVALID_NOT_SEMANTIC


@pytest.mark.parametrize(
    ["version1", "version2"],
    zip(  # loop over pairs of neighboring elements
        VALID_AND_NORMALIZED_VERSIONS,
        VALID_AND_NORMALIZED_VERSIONS[1:],
    ),
)
def test_versions_are_strictly_ordered(version1, version2):
    """`VALID_AND_NORMALIZED_VERSIONS` are ordered."""
    version1_parsed = pkg_version.Version(version1)
    version2_parsed = pkg_version.Version(version2)

    assert version1_parsed < version2_parsed


@pytest.mark.parametrize(
    ["version1", "version2"],
    zip(  # loop over pairs of neighboring elements
        VALID_AND_NOT_NORMALIZED_VERSIONS,
        VALID_AND_NOT_NORMALIZED_VERSIONS[1:],
    ),
)
def test_versions_are_weakly_ordered(version1, version2):
    """`VALID_AND_NOT_NORMALIZED_VERSIONS` are ordered."""
    version1_parsed = pkg_version.Version(version1)
    version2_parsed = pkg_version.Version(version2)

    assert version1_parsed <= version2_parsed


class VersionClassification:
    """Classifying version identifiers.

    There are four distinct kinds of version identifiers:
     - "X.Y.Z.devN" => developmental non-releases
     - "X.Y.Z[aN|bN|rcN]" => pre-releases (e.g., alpha, beta, or release candidates)
     - "X.Y.Z" => ordinary (or "official) releases to PypI
     - "X.Y.Z.postN" => post-releases (e.g., to add missing non-code artifacts)

    The `packaging` library models these four cases slightly different, and,
    most notably in an overlapping fashion (i.e., developmental releases are
    also pre-releases).

    The four methods in this class introduce our own logic
    treating the four cases in a non-overlapping fashion.
    """

    def is_dev_release(self, parsed_version):
        """A "X.Y.Z.devN" release."""
        is_so_by_parts = (
            parsed_version.dev is not None
            and parsed_version.pre is None
            and parsed_version.post is None
        )

        if is_so_by_parts:
            assert parsed_version.is_devrelease is True
            assert parsed_version.is_prerelease is True
            assert parsed_version.is_postrelease is False

        return is_so_by_parts

    def is_pre_release(self, parsed_version):
        """A "X.Y.Z[aN|bN|rcN]" release."""
        is_so_by_parts = (
            parsed_version.dev is None
            and parsed_version.pre is not None
            and parsed_version.post is None
        )

        if is_so_by_parts:
            assert parsed_version.is_devrelease is False
            assert parsed_version.is_prerelease is True
            assert parsed_version.is_postrelease is False

        return is_so_by_parts

    def is_ordinary_release(self, parsed_version):
        """A "X.Y.Z" release."""
        is_so_by_parts = (
            parsed_version.dev is None
            and parsed_version.pre is None
            and parsed_version.post is None
        )

        if is_so_by_parts:
            assert parsed_version.is_devrelease is False
            assert parsed_version.is_prerelease is False
            assert parsed_version.is_postrelease is False

        return is_so_by_parts

    def is_post_release(self, parsed_version):
        """A "X.Y.Z.postN" release."""
        is_so_by_parts = (
            parsed_version.dev is None
            and parsed_version.pre is None
            and parsed_version.post is not None
        )

        if is_so_by_parts:
            assert parsed_version.is_devrelease is False
            assert parsed_version.is_prerelease is False
            assert parsed_version.is_postrelease is True

        return is_so_by_parts


class TestVersionIdentifier(VersionClassification):
    """The versions must comply with PEP440 ...

    and follow some additional constraints, most notably that a version's
    base complies with semantic versioning.
    """

    def test_packaged_version_is_declared_version(self):
        """`lalib.__version__` matches "version" in pyproject.toml exactly."""
        assert PACKAGED_VERSION == DECLARED_VERSION

    @pytest.fixture
    def parsed_version(self, request):
        """A version identifier parsed with `packaging.version.Version()`."""
        return pkg_version.Version(request.param)

    @pytest.fixture
    def unparsed_version(self, request):
        """A version identifier represented as an ordinary `str`."""
        return request.param

    @pytest.mark.parametrize("unparsed_version", INVALID_NOT_READABLE)
    def test_does_not_follow_pep440(self, unparsed_version):
        """A version's base does not follow PEP440."""
        with pytest.raises(pkg_version.InvalidVersion):
            pkg_version.Version(unparsed_version)

    @pytest.mark.parametrize(
        ["parsed_version", "unparsed_version"],
        [(v, v) for v in VALID_VERSIONS],
        indirect=True,
    )
    def test_base_follows_semantic_versioning(self, parsed_version, unparsed_version):
        """A version's base follows semantic versioning."""
        result = semver.Version.parse(parsed_version.base_version)
        result = str(result)

        assert unparsed_version.startswith(result)

    @pytest.mark.parametrize("version", INVALID_NOT_READABLE + INVALID_NOT_SEMANTIC)
    def test_base_does_not_follow_semantic_versioning(self, version):
        """A version's base does not follow semantic versioning."""
        with pytest.raises(ValueError, match="not valid SemVer"):
            semver.Version.parse(version)

    @pytest.mark.parametrize("parsed_version", VALID_VERSIONS, indirect=True)
    def test_has_major_minor_patch_parts(self, parsed_version):
        """A version's base consists of three parts."""
        three_parts = 3

        assert len(parsed_version.release) == three_parts

    @pytest.mark.parametrize("parsed_version", VALID_VERSIONS, indirect=True)
    @pytest.mark.parametrize("part", ["major", "minor", "micro"])
    def test_major_minor_patch_parts_are_within_range(self, parsed_version, part):
        """A version's "major", "minor", and "patch" parts are non-negative and `< 100`."""
        # "micro" in PEP440 is "patch" in semantic versioning
        part = getattr(parsed_version, part, -1)
        two_digits_only = 100

        assert 0 <= part < two_digits_only

    @pytest.mark.parametrize("parsed_version", VALID_VERSIONS, indirect=True)
    def test_is_either_dev_pre_post_or_ordinary_release(self, parsed_version):
        """A version is exactly one of four kinds."""
        result = (  # `bool`s behaving like `int`s
            self.is_dev_release(parsed_version)
            + self.is_pre_release(parsed_version)
            + self.is_ordinary_release(parsed_version)
            + self.is_post_release(parsed_version)
        )

        assert result == 1

    @pytest.mark.parametrize("parsed_version", VALID_VERSIONS, indirect=True)
    def test_dev_releases_come_with_dev0(self, parsed_version):
        """A ".devN" version always comes with ".dev0"."""
        if self.is_dev_release(parsed_version):
            assert parsed_version.dev == 0
            assert parsed_version.pre is None
            assert parsed_version.post is None
        else:
            assert parsed_version.dev is None

    @pytest.mark.parametrize("parsed_version", VALID_VERSIONS, indirect=True)
    def test_pre_releases_come_with_suffix1_or_suffix2(self, parsed_version):
        """A "aN", "bN", or "rcN" version always comes with N as 1 or 2."""
        if self.is_pre_release(parsed_version):
            assert parsed_version.dev is None
            assert parsed_version.pre[1] in (1, 2)
            assert parsed_version.post is None
        else:
            assert parsed_version.pre is None

    @pytest.mark.parametrize("parsed_version", VALID_VERSIONS, indirect=True)
    def test_ordinary_releases_have_no_suffixes(self, parsed_version):
        """A ordinary release versions has no suffixes."""
        if self.is_ordinary_release(parsed_version):
            assert parsed_version.dev is None
            assert parsed_version.pre is None
            assert parsed_version.post is None

    @pytest.mark.parametrize("parsed_version", VALID_VERSIONS, indirect=True)
    def test_post_releases_come_with_post0_to_post9(self, parsed_version):
        """A ".postN" version always comes with N as 0 through 9."""
        if self.is_post_release(parsed_version):
            assert parsed_version.dev is None
            assert parsed_version.pre is None
            assert parsed_version.post in range(10)
        else:
            assert parsed_version.post is None

    @pytest.mark.parametrize("parsed_version", VALID_VERSIONS, indirect=True)
    def test_has_no_epoch_segment(self, parsed_version):
        """A version has no epoch segment."""
        assert parsed_version.epoch == 0

    @pytest.mark.parametrize("parsed_version", VALID_VERSIONS, indirect=True)
    def test_has_no_local_segment(self, parsed_version):
        """A parsed_version has no local segment.

        In semantic versioning, the "local" segment is referred
        to as the "build metadata".
        """
        assert parsed_version.local is None

    @pytest.mark.parametrize(
        ["parsed_version", "unparsed_version"],
        [
            (v, v)
            for v in (
                DECLARED_VERSION,
                PACKAGED_VERSION,
                *VALID_AND_NORMALIZED_VERSIONS,
            )
        ],
        indirect=True,
    )
    def test_is_normalized(self, parsed_version, unparsed_version):
        """A version is already normalized.

        For example, a version cannot be "1.2.3.a1"
        because this gets normalized into "1.2.3a1".
        """
        assert parsed_version.public == unparsed_version

    @pytest.mark.parametrize(
        ["parsed_version", "unparsed_version"],
        [(v, v) for v in VALID_AND_NOT_NORMALIZED_VERSIONS],
        indirect=True,
    )
    def test_is_not_normalized(self, parsed_version, unparsed_version):
        """A version is not yet normalized.

        For example, the version "1.2.3.a1"
        gets normalized into "1.2.3a1".
        """
        assert parsed_version.public != unparsed_version


class TestVersionIdentifierWithPattern:
    """Test the versioning with a custom `regex` pattern."""

    x_y_z_version = r"^(0|([1-9]\d*))\.(0|([1-9]\d*))\.(0|([1-9]\d*))"
    suffixes = r"((\.dev0)|(((a)|(b)|(rc))(1|2))|(\.post\d{1}))"
    version_pattern = re.compile(f"^{x_y_z_version}{suffixes}?$")

    @pytest.mark.parametrize(
        "version",
        [
            DECLARED_VERSION,
            PACKAGED_VERSION,
        ],
    )
    def test_packaged_and_declared_version(self, version):
        """Packaged version follows PEP440 and semantic versioning."""
        result = self.version_pattern.fullmatch(version)

        assert result is not None

    # The next two test cases are sanity checks to validate the `version_pattern`.

    @pytest.mark.parametrize("version", VALID_AND_NORMALIZED_VERSIONS)
    def test_valid_versioning(self, version):
        """A version follows the "x.y.z[.devN|aN|bN|rcN|.postN]" format."""
        result = self.version_pattern.fullmatch(version)

        assert result is not None

    @pytest.mark.parametrize("version", INVALID_VERSIONS)
    def test_invalid_versioning(self, version):
        """A version does not follow the "x.y.z[.devN|aN|bN|rcN|.postN]" format."""
        result = self.version_pattern.fullmatch(version)

        assert result is None


class TestUnavailablePackageMetadata:
    """Pretend only source files are available, without metadata."""

    def find_path_to_package_metadata_folder(self, name):
        """Find the path to a locally installed package within a `venv`."""
        paths = tuple(
            itertools.chain(
                *(pathlib.Path(path).glob(f"{name}-*.dist-info/") for path in sys.path),
            ),
        )

        # Sanity Check: There must be exactly one folder
        # for an installed package within a virtual environment
        assert len(paths) == 1

        return pathlib.Path(paths[0]).relative_to(pathlib.Path.cwd())

    @contextlib.contextmanager
    def hide_metadata_from_package(self, name):
        """Hide the metadata of a locally installed package."""
        # Rename the metadata folder
        path = self.find_path_to_package_metadata_folder(name)
        path.rename(str(path).replace(name, f"{name}.tmp"))

        # (Re-)Load the package with missing metadata
        package = importlib.import_module(name)
        importlib.reload(package)

        try:
            yield package

        finally:
            # Restore the original metadata folder
            path = self.find_path_to_package_metadata_folder(f"{name}.tmp")
            path = path.rename(str(path).replace(f"{name}.tmp", name))

            # Reload the package with the original metadata for other tests
            importlib.reload(package)

    def test_package_without_version_info(self):
        """Import `lalib` with no available version info."""
        with self.hide_metadata_from_package("lalib") as lalib_pkg:
            assert lalib_pkg.__pkg_name__ == "unknown"
            assert lalib_pkg.__version__ == "unknown"
