"""Configure nox to run maintenance tasks in isolated environments.

For local development, use the following sessions:
    - "format" => run autoflake, black, and isort to format the code nicely
    - "lint" => run flake8 and mypy to lint the code base
"""

import os
import tempfile
from typing import Any

import nox


# Python version with which the project is developed.
MAIN_PYTHON = '3.8'

# Make the project forward compatible.
SUPPORTED_PYTHONS = (MAIN_PYTHON, '3.9')

# Paths with *.py files.
SRC_LOCATIONS = 'noxfile.py', 'src/'


# Use a unified cache folder for all develop tools.
nox.options.envdir = '.cache/nox'

# All tools except git and poetry are project dependencies.
# Avoid accidental successes if the environment is not set up properly.
nox.options.error_on_external_run = True

# Run only CI related checks by default.
nox.options.sessions = (
    'format',
    'lint',
    *(f'test-{version}' for version in SUPPORTED_PYTHONS),
)


@nox.session(name='format', python=MAIN_PYTHON)
def format_(session: nox.Session) -> None:
    """Format the source files with autoflake, black, and isort."""
    _show_info(session)
    _install_packages(session, 'autoflake', 'black', 'isort')

    # Interpret extra arguments as locations of source files.
    locations = session.posargs or SRC_LOCATIONS

    session.run('autoflake', '--version')
    session.run(
        'autoflake',
        '--in-place',
        '--recursive',
        '--expand-star-imports',
        '--remove-all-unused-imports',
        '--ignore-init-module-imports',  # modifies --remove-all-unused-imports
        '--remove-duplicate-keys',
        '--remove-unused-variables',
        *locations,
    )

    session.run('black', '--version')
    session.run('black', *locations)

    session.run('isort', '--version')
    session.run('isort', *locations)


@nox.session(python=MAIN_PYTHON)
def lint(session: nox.Session) -> None:
    """Lint the source files with flake8 and mypy."""
    _show_info(session)
    _install_packages(
        session,
        'flake8',
        'flake8-annotations',
        'flake8-black',
        'flake8-expression-complexity',
        'mypy',
        'wemake-python-styleguide',
    )

    # Interpret extra arguments as locations of source files.
    locations = session.posargs or SRC_LOCATIONS

    session.run('flake8', '--version')
    session.run('flake8', *locations)

    # For mypy, only lint *.py files to be packaged.
    mypy_locations = [path for path in locations if path.startswith(SRC_LOCATIONS)]
    if mypy_locations:
        session.run('mypy', '--version')
        session.run('mypy', *mypy_locations)
    else:
        session.log('No paths to be checked with mypy')


@nox.session(python=SUPPORTED_PYTHONS)
def test(session: nox.Session) -> None:
    """Test the code base."""
    _show_info(session)


def _show_info(session: nox.Session) -> None:
    """Show generic info about a session."""
    if session.posargs:
        print('extra arguments:', *session.posargs)  # noqa:WPS421

    session.run('python', '--version')

    # Fake GNU's pwd.
    session.log('pwd')
    print(os.getcwd())  # noqa:WPS421


def _install_packages(
    session: nox.Session,
    *packages_or_pip_args: str,
    **kwargs: Any,
) -> None:
    """Install packages respecting the "poetry.lock" file.

    This function wraps nox.Session.install() such that it installs
    packages respecting the pinned versions specified in poetry's lock file.
    This makes nox sessions more deterministic.

    IMPORTANT: Package installation is skipped if the `session` is run with
    the "-r" flag to re-use an existing virtual environment. That turns nox
    into a fast task runner provided that a virtual environment already exists.

    Args:
        session: the Session object
        *packages_or_pip_args: the packages to be installed or pip options
        **kwargs: passed on to `nox.Session.install()`
    """
    if session.virtualenv.reuse_existing:
        session.log(
            'No dependencies are installed as an existing environment is re-used',
        )
        return

    session.log('Dependencies are installed respecting the poetry.lock file')

    with tempfile.NamedTemporaryFile() as requirements_txt:
        session.run(
            'poetry',
            'export',
            '--dev',
            '--format=requirements.txt',
            f'--output={requirements_txt.name}',
            '--without-hashes',
            external=True,
        )
        session.install(
            f'--constraint={requirements_txt.name}',
            *packages_or_pip_args,
            **kwargs,
        )
