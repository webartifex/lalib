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

DOCS_SRC, DOCS_BUILD = ("docs/", ".cache/docs/")
TESTS_LOCATION = "tests/"
SRC_LOCATIONS = ("./noxfile.py", "src/", DOCS_SRC, TESTS_LOCATION)


nox.options.envdir = ".cache/nox"
nox.options.error_on_external_run = True  # only `git` and `poetry` are external
nox.options.reuse_venv = "no"
nox.options.sessions = (  # run by default when invoking `nox` on the CLI
    "format",
    "lint",
    "audit",
    "docs",
    "test-docstrings",
    f"test-{MAIN_PYTHON}",
)
nox.options.stop_on_first_error = True


@nox_session(name="audit", python=MAIN_PYTHON, reuse_venv=False)
def audit_pinned_dependencies(session: nox.Session) -> None:
    """Check dependencies for vulnerabilities with `pip-audit`.

    The dependencies are those defined in the "poetry.lock" file.

    `pip-audit` uses the Python Packaging Advisory Database
    (Source: https://github.com/pypa/advisory-database).
    """
    do_not_reuse(session)
    start(session)

    install_unpinned(session, "pip-audit")

    session.run("pip-audit", "--version")
    suppress_poetry_export_warning(session)
    with tempfile.NamedTemporaryFile() as requirements_txt:
        session.run(
            "poetry",
            "export",
            "--format=requirements.txt",
            f"--output={requirements_txt.name}",
            "--with=dev",
            external=True,
        )
        session.run(
            "pip-audit",
            f"--requirement={requirements_txt.name}",
            "--local",
            "--progress-spinner=off",
            "--strict",
        )


@nox_session(name="audit-updates", python=MAIN_PYTHON, reuse_venv=False)
def audit_unpinned_dependencies(session: nox.Session) -> None:
    """Check updates for dependencies with `pip-audit`.

    Convenience task to check dependencies before updating
    them in the "poetry.lock" file.

    Uses `pip` to resolve the dependencies declared in the
    "pyproject.toml" file (incl. the "dev" group) to their
    latest PyPI version.
    """
    do_not_reuse(session)
    start(session)

    pyproject = load_pyproject_toml()
    poetry_config = pyproject["tool"]["poetry"]

    dependencies = {
        *(poetry_config["dependencies"].keys()),
        *(poetry_config["group"]["dev"]["dependencies"].keys()),
    }
    dependencies.discard("python")  # Python itself cannot be installed f>

    install_unpinned(session, "pip-audit", *sorted(dependencies))
    session.run("pip-audit", "--version")
    session.run(
        "pip-audit",
        "--local",
        "--progress-spinner=off",
        "--strict",
    )


@nox_session(python=MAIN_PYTHON)
def docs(session: nox.Session) -> None:
    """Build the documentation with `sphinx`."""
    start(session)

    # The documentation tools require the developed package as
    # otherwise sphinx's autodoc could not include the docstrings
    session.debug("Install only the `lalib` package and the documentation tools")
    install_unpinned(session, "-e", ".")  # editable to be able to reuse the session
    install_pinned(session, "sphinx", "sphinx-autodoc-typehints")

    session.run("sphinx-build", "--builder=html", DOCS_SRC, DOCS_BUILD)
    session.run("sphinx-build", "--builder=linkcheck", DOCS_SRC, DOCS_BUILD)  # > 200 OK

    session.log(f"Docs are available at {DOCS_BUILD}index.html")


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

    # If this function is run by the `pre-commit` framework, extra
    # arguments are dropped by the hack inside `pre_commit_test_hook()`
    posargs = () if session.env.get("_drop_posargs") else session.posargs
    args = posargs or (
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


@nox_session(name="pre-commit-install", python=MAIN_PYTHON, venv_backend="none")
def pre_commit_install(session: nox.Session) -> None:
    """Install `pre-commit` hooks."""
    for type_ in ("pre-commit", "pre-merge-commit"):
        session.run(
            "poetry",
            "run",
            "pre-commit",
            "install",
            f"--hook-type={type_}",
            external=True,
        )


@nox_session(name="_pre-commit-test-hook", python=MAIN_PYTHON, reuse_venv=False)
def pre_commit_test_hook(session: nox.Session) -> None:
    """`pre-commit` hook to run all tests before merges.

    Ignores the paths to the staged files passed in by the
    `pre-commit` framework and executes all tests instead. So,
    `nox -s _pre-commit-test-hook -- FILE1, ...` drops the "FILE1, ...".
    """
    do_not_reuse(session)

    # Little Hack: Create a flag in the env(ironment) ...
    session.env["_drop_posargs"] = "true"

    # ... and call `test()` directly because `session.notify()`
    # creates the "test" session as a new `nox.Session` object
    # that does not have the flag set
    test(session)


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


def suppress_poetry_export_warning(session: nox.Session) -> None:
    """Temporary fix to avoid poetry's warning ...

    ... about "poetry-plugin-export not being installed in the future".
    """
    session.run(
        "poetry",
        "config",
        "--local",
        "warnings.export",
        "false",
        external=True,
        log=False,  # because it's just a fix we don't want any message in the logs
    )


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

    suppress_poetry_export_warning(session)

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
