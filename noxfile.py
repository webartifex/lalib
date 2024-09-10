"""Maintenance tasks run in isolated environments."""

import collections
import pathlib
import random
import re
import tempfile
from collections.abc import Mapping
from typing import Any

import nox
from packaging import version as pkg_version


try:
    from nox_poetry import session as nox_session
except ImportError:
    nox_session = nox.session
    nox_poetry_available = False
else:
    nox_poetry_available = True


def nested_defaultdict() -> collections.defaultdict[str, Any]:
    """Create a multi-level `defaultdict` with variable depth.

    The returned `dict`ionary never raises a `KeyError`
    but always returns an empty `dict`ionary instead.
    This behavior is occurs recursively.

    Adjusted from: https://stackoverflow.com/a/8702435
    """
    return collections.defaultdict(nested_defaultdict)


def defaultify(obj: Any) -> Any:
    """Turn nested `dict`s into nested `defaultdict`s."""
    if isinstance(obj, Mapping):
        return collections.defaultdict(
            nested_defaultdict,
            {key: defaultify(val) for key, val in obj.items()},
        )
    return obj


def load_pyproject_toml() -> collections.defaultdict[str, Any]:
    """Load the contents of the pyproject.toml file.

    The contents are represented as a `nested_defaultdict`;
    so, missing keys and tables (i.e., "sections" in the .ini format)
    do not result in `KeyError`s but return empty `nested_defaultdict`s.
    """
    return defaultify(nox.project.load_toml("pyproject.toml"))


def load_supported_python_versions(*, reverse: bool = False) -> list[str]:
    """Parse the Python versions from the pyproject.toml file."""
    pyproject = load_pyproject_toml()
    version_names = {
        classifier.rsplit(" ")[-1]
        for classifier in pyproject["tool"]["poetry"]["classifiers"]
        if classifier.startswith("Programming Language :: Python :: ")
    }
    return sorted(version_names, key=pkg_version.Version, reverse=reverse)


SUPPORTED_PYTHONS = load_supported_python_versions(reverse=True)
MAIN_PYTHON = "3.12"

TESTS_LOCATION = "tests/"
SRC_LOCATIONS = ("./noxfile.py", "src/", TESTS_LOCATION)


nox.options.envdir = ".cache/nox"
nox.options.error_on_external_run = True  # only `git` and `poetry` are external
nox.options.reuse_venv = "no"
nox.options.sessions = (  # run by default when invoking `nox` on the CLI
    "format",
    "lint",
    "test-docstrings",
    f"test-{MAIN_PYTHON}",
)
nox.options.stop_on_first_error = True


@nox_session(name="format", python=MAIN_PYTHON)
def format_(session: nox.Session) -> None:
    """Format source files with `autoflake`, `black`, and `isort`."""
    start(session)

    install_pinned(session, "autoflake", "black", "isort", "ruff")

    locations = session.posargs or SRC_LOCATIONS

    session.run("autoflake", "--version")
    session.run("autoflake", *locations)

    session.run("black", "--version")
    session.run("black", *locations)

    session.run("isort", "--version-number")
    session.run("isort", *locations)

    session.run("ruff", "--version")
    session.run("ruff", "check", "--fix-only", *locations)


@nox_session(python=MAIN_PYTHON)
def lint(session: nox.Session) -> None:
    """Lint source files with `flake8`, `mypy`, and `ruff`."""
    start(session)

    install_pinned(
        session,
        "flake8",
        "flake8-annotations",
        "flake8-bandit",
        "flake8-black",
        "flake8-broken-line",
        "flake8-bugbear",
        "flake8-commas",
        "flake8-comprehensions",
        "flake8-debugger",
        "flake8-docstrings",
        "flake8-eradicate",
        "flake8-isort",
        "flake8-quotes",
        "flake8-string-format",
        "flake8-pyproject",
        "flake8-pytest-style",
        "mypy",
        "pep8-naming",  # flake8 plug-in
        "pydoclint[flake8]",
        "ruff",
    )

    locations = session.posargs or SRC_LOCATIONS

    session.run("flake8", "--version")
    session.run("flake8", *locations)

    session.run("mypy", "--version")
    session.run("mypy", *locations)

    session.run("ruff", "--version")
    session.run("ruff", "check", *locations)


TEST_DEPENDENCIES = (
    "packaging",
    "pytest",
    "pytest-cov",
    "semver",
    "xdoctest",
)


@nox_session(python=SUPPORTED_PYTHONS)
def test(session: nox.Session) -> None:
    """Test code with `pytest`."""
    start(session)

    install_unpinned(session, "-e", ".")  # "-e" makes session reuseable
    install_pinned(session, *TEST_DEPENDENCIES)

    args = session.posargs or (
        "--cov",
        "--no-cov-on-fail",
        TESTS_LOCATION,
    )

    session.run("pytest", *args)


_magic_number = random.randint(0, 987654321)  # noqa: S311


@nox_session(name="test-coverage", python=MAIN_PYTHON, reuse_venv=True)
def test_coverage(session: nox.Session) -> None:
    """Report the combined coverage statistics.

    Run the test suite for all supported Python versions
    and combine the coverage statistics.
    """
    install_pinned(session, "coverage")

    session.run("python", "-m", "coverage", "erase")

    for version in SUPPORTED_PYTHONS:
        session.notify(f"_test-coverage-run-{version}", (_magic_number,))
    session.notify("_test-coverage-report", (_magic_number,))


@nox_session(name="_test-coverage-run", python=SUPPORTED_PYTHONS, reuse_venv=False)
def test_coverage_run(session: nox.Session) -> None:
    """Measure the test coverage."""
    do_not_reuse(session)
    do_not_run_directly(session)

    start(session)

    session.install(".")
    install_pinned(session, "coverage", *TEST_DEPENDENCIES)

    session.run(
        "python",
        "-m",
        "coverage",
        "run",
        "-m",
        "pytest",
        TESTS_LOCATION,
    )


@nox_session(name="_test-coverage-report", python=MAIN_PYTHON, reuse_venv=True)
def test_coverage_report(session: nox.Session) -> None:
    """Report the combined coverage statistics."""
    do_not_run_directly(session)

    install_pinned(session, "coverage")

    session.run("python", "-m", "coverage", "combine")
    session.run("python", "-m", "coverage", "report", "--fail-under=100")


@nox_session(name="test-docstrings", python=MAIN_PYTHON)
def test_docstrings(session: nox.Session) -> None:
    """Test docstrings with `xdoctest`."""
    start(session)
    install_pinned(session, "xdoctest[colors]")

    session.run("xdoctest", "--version")
    session.run("xdoctest", "src/lalib")


def do_not_reuse(session: nox.Session, *, raise_error: bool = True) -> None:
    """Do not reuse a session with the "-r" flag."""
    if session._runner.venv._reused:  # noqa:SLF001
        if raise_error:
            session.error('The session must be run without the "-r" flag')
        else:
            session.warn('The session must be run without the "-r" flag')


def do_not_run_directly(session: nox.Session) -> None:
    """Do not run a session with `nox -s SESSION_NAME` directly."""
    if not session.posargs or session.posargs[0] != _magic_number:
        session.error("This session must not be run directly")


def start(session: nox.Session) -> None:
    """Show generic info about a session."""
    if session.posargs:
        session.debug(f"Received extra arguments: {session.posargs}")

    session.debug("Some generic information about the environment")
    session.run("python", "--version")
    session.run("python", "-c", "import sys; print(sys.executable)")
    session.run("python", "-c", "import sys; print(sys.path)")
    session.run("python", "-c", "import os; print(os.getcwd())")
    session.run("python", "-c", 'import os; print(os.environ["PATH"])')

    session.env["BLACK_CACHE_DIR"] = ".cache/black"
    session.env["PIP_CACHE_DIR"] = ".cache/pip"
    session.env["PIP_DISABLE_PIP_VERSION_CHECK"] = "true"


def install_pinned(
    session: nox.Session,
    *packages_or_pip_args: str,
    **kwargs: Any,
) -> None:
    """Install packages respecting the "poetry.lock" file.

    Wraps `nox.sessions.Session.install()` such that it installs
    packages respecting the pinned versions specified in poetry's
    lock file. This makes nox sessions more deterministic.
    """
    session.debug("Install packages respecting the poetry.lock file")

    session.run(  # temporary fix to avoid poetry's future warning
        "poetry",
        "config",
        "--local",
        "warnings.export",
        "false",
        external=True,
        log=False,  # because it's just a fix
    )

    if nox_poetry_available:
        session.install(*packages_or_pip_args, **kwargs)
        return

    with tempfile.NamedTemporaryFile() as requirements_txt:
        session.run(
            "poetry",
            "export",
            "--format=requirements.txt",
            f"--output={requirements_txt.name}",
            "--with=dev",
            "--without-hashes",
            external=True,
        )

        # `pip install --constraint ...` raises an error if the
        # dependencies in requirements.txt contain "extras"
        # => Strip "package[extras]==1.2.3" into "package==1.2.3"
        dependencies = pathlib.Path(requirements_txt.name).read_text().split("\n")
        dependencies = [re.sub(r"\[.*\]==", "==", dep) for dep in dependencies]
        pathlib.Path(requirements_txt.name).write_text("\n".join(dependencies))

        session.install(
            f"--constraint={requirements_txt.name}",
            *packages_or_pip_args,
            **kwargs,
        )


def install_unpinned(
    session: nox.Session,
    *packages_or_pip_args: str,
    **kwargs: Any,
) -> None:
    """Install the latest PyPI versions of packages."""
    # Same logic to skip package installation as in core nox
    # See: https://github.com/wntrblm/nox/blob/2024.04.15/nox/sessions.py#L775
    venv = session._runner.venv  # noqa: SLF001
    if session._runner.global_config.no_install and venv._reused:  # noqa: SLF001
        return

    if kwargs.get("silent") is None:
        kwargs["silent"] = True

    # Cannot use `session.install(...)` here because
    # with "nox-poetry" installed this leads to an
    # installation respecting the "poetry.lock" file
    session.run(
        "python",
        "-m",
        "pip",
        "install",
        *packages_or_pip_args,
        **kwargs,
    )


if MAIN_PYTHON not in SUPPORTED_PYTHONS:
    msg = f"MAIN_PYTHON version, v{MAIN_PYTHON}, is not in SUPPORTED_PYTHONS"
    raise RuntimeError(msg)
