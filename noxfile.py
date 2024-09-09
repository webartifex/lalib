"""Maintenance tasks run in isolated environments."""

import collections
from collections.abc import Mapping
from typing import Any

import nox
from packaging import version as pkg_version


try:
    from nox_poetry import session as nox_session
except ImportError:
    nox_session = nox.session


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

SRC_LOCATIONS = ("./noxfile.py", "src/")


nox.options.envdir = ".cache/nox"
nox.options.error_on_external_run = True  # only `git` and `poetry` are external
nox.options.reuse_venv = "no"
nox.options.sessions = (  # run by default when invoking `nox` on the CLI
)
nox.options.stop_on_first_error = True


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

    session.env["PIP_CACHE_DIR"] = ".cache/pip"
    session.env["PIP_DISABLE_PIP_VERSION_CHECK"] = "true"


if MAIN_PYTHON not in SUPPORTED_PYTHONS:
    msg = f"MAIN_PYTHON version, v{MAIN_PYTHON}, is not in SUPPORTED_PYTHONS"
    raise RuntimeError(msg)
