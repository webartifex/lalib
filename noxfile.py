"""Configure nox to run maintenance tasks in isolated environments.

For local development, use the following sessions:
    - "init-project" => set up local pre-commit hooks (see below)
    - "format" => run autoflake, black, and isort to format the code nicely
    - "lint" => run flake8 and mypy to lint the code base
    - "test-x.y" => run the test suite for Python version x.y

The `pre-commit` framework invokes the following tasks:
    - before any commit:
      + "format" => as above
      + "lint" => as above
    - before merges => run the entire "test-suite"
"""

import os
import tempfile
from typing import Any

import nox


# Python version with which the project is developed.
MAIN_PYTHON = '3.8'

# Make the project forward compatible.
SUPPORTED_PYTHONS = (MAIN_PYTHON, '3.9')

# Path to the test suite.
TESTS_FOLDER = 'tests/'

# Paths with *.py files.
SRC_LOCATIONS = ('noxfile.py', 'src/', TESTS_FOLDER)


# Use a unified cache folder for all develop tools.
nox.options.envdir = '.cache/nox'

# All tools except git and poetry are project dependencies.
# Avoid accidental successes if the environment is not set up properly.
nox.options.error_on_external_run = True

# Run only CI related checks by default.
nox.options.sessions = (
    'format',
    'lint',
    'safety',
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
        'flake8-pytest-style',
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


@nox.session(python=MAIN_PYTHON)
def safety(session: nox.Session) -> None:
    """Check the dependencies for known security vulnerabilities."""
    _show_info(session)

    # We do not pin the version of `safety` to always check with the
    # latest version. The risk of this breaking the CI is rather low.
    session.install('safety')

    with tempfile.NamedTemporaryFile() as requirements_txt:
        session.run(
            'poetry',
            'export',
            '--dev',
            '--format=requirements.txt',
            f'--output={requirements_txt.name}',
            external=True,
        )
        session.run(
            'safety',
            'check',
            f'--file={requirements_txt.name}',
            '--full-report',
        )


@nox.session(python=SUPPORTED_PYTHONS)
def test(session: nox.Session) -> None:
    """Test the code base."""
    # Re-using an old environment is not deterministic here as
    # `poetry install --no-dev` removes previously installed packages.
    if session.virtualenv.reuse_existing:
        raise RuntimeError('The "test-*" sessions must be run without the "-r" option')

    _show_info(session)

    # Install only the `lalib` package and the testing tool chain.
    session.run('poetry', 'install', '--no-dev', external=True)
    _install_packages(session, 'packaging', 'pytest', 'pytest-cov')

    # Interpret extra arguments as options for pytest.
    # They are "dropped" by the hack in the `test_suite()` function
    # if this function is run within the "test-suite" session.
    posargs = () if session.env.get('_drop_posargs') else session.posargs
    args = posargs or (
        '--cov',
        '--no-cov-on-fail',
        '--cov-branch',
        '--cov-fail-under=100',
        '--cov-report=term-missing:skip-covered',
        TESTS_FOLDER,
    )

    session.run('pytest', *args)


@nox.session(name='test-suite', python=MAIN_PYTHON)
def test_suite(session: nox.Session) -> None:
    """Run the entire test suite.

    Intended to be run as a pre-commit hook!

    Ignores the paths to the staged files passed in by the
    `pre-commit` framework and executes all tests instead.
    """
    # Re-using an old environment is not deterministic here as
    # `poetry install --no-dev` removes previously installed packages.
    if session.virtualenv.reuse_existing:
        raise RuntimeError(
            'The "test-suite" session must be run without the "-r" option',
        )

    # Little hack to ignore the extra arguments provided
    # by the `pre-commit` framework. Create a flag in the
    # env(ironment) that must contain only `str`-like objects.
    session.env['_drop_posargs'] = 'true'

    # Cannot use `session.notify()` to trigger the "test" session as
    # that would create a new `nox.Session` object without the flag in
    # the environment. Instead, run the `test()` function from here.
    test(session)


@nox.session(name='init-project', python=MAIN_PYTHON, venv_backend='none')
def init_project(session: nox.Session) -> None:
    """Install the pre-commit hooks."""
    for type_ in ('pre-commit', 'pre-merge-commit'):
        session.run(
            'poetry',
            'run',
            'pre-commit',
            'install',
            f'--hook-type={type_}',
            external=True,
        )


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
