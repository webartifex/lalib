"""Configure nox to run maintenance tasks in isolated environments.

For local development, use the following sessions:

- "format" => run autoflake, black, and isort to format the code nicely
- "lint" => run flake8, mypy, and pylint to check the code base
- "docs" => build the docs with sphinx
- "test-3.7" / "test-3.8" => run the test suite
- "clean-pwd" => remove all temporary files from the project folder

The pre-commit framework invokes the following tasks:

- before any commit:

  + "format" => as above
  + "lint" => as above

- before merges: run the entire "test-suite" independent of the file changes
"""

import contextlib
import glob
import os
import re
import shutil
import subprocess  # noqa:S404
import tempfile
from typing import Any, Generator, IO, Tuple

import nox
from nox import sessions


PACKAGE_NAME = 'lalib'
GITHUB_REPOSITORY = f'webartifex/{PACKAGE_NAME}'

# Python version with which the project is developed.
MAIN_PYTHON = '3.8'

# Keep the project backwards compatible.
SUPPORTED_PYTHONS = ('3.7', MAIN_PYTHON)

# Docs/sphinx locations.
DOCS_SRC = 'docs/'
DOCS_BUILD = '.cache/docs/'

# Path where the package lies.
SRC_FOLDER = 'src/'

# Path to the test suite.
TESTS_FOLDER = 'tests/'

# Paths with *.py files.
SRC_LOCATIONS = (f'{DOCS_SRC}/conf.py', 'noxfile.py', SRC_FOLDER, TESTS_FOLDER)


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
    'docs',
    *(f'test-{version}' for version in SUPPORTED_PYTHONS),
    'test-docstrings',
)


@nox.session(name='fix-branch-references', python=MAIN_PYTHON, venv_backend='none')
def fix_branch_references(session: sessions.Session) -> None:  # noqa:WPS210,WPS231
    """Replace branch references with the current branch.

    Intended to be run as a pre-commit hook.

    Many files in the project (e.g., README.md) contain links to resources
    on github.com or other sites that contain branch labels.

    This task rewrites these links such that they contain branch references
    that make sense given the context:

    - If the branch is only a temporary one that is to be merged into
      the 'main' branch, all references are adjusted to 'main' as well.
    - If the branch is not named after a default branch in the GitFlow
      model, it is interpreted as a feature branch and the references
      are adjusted into 'develop'.

    This task may be called with one positional argument that is interpreted
    as the branch to which all references are changed into.
    The format must be "--branch=BRANCH_NAME".
    """
    # Adjust this to add/remove glob patterns
    # whose links are re-written.
    paths = ['*.md', '**/*.md']

    # Get the branch git is currently on.
    # This is the branch to which all references are changed into
    # if none of the two exceptions below apply.
    branch = (
        subprocess.check_output(  # noqa:S603
            ('git', 'rev-parse', '--abbrev-ref', 'HEAD'),
        )
        .decode()
        .strip()
    )

    # If the current branch is only a temporary one that is to be merged
    # into 'main', we adjust all branch references to 'main' as well.
    if branch.startswith('release-') or branch.startswith('hotfix-'):
        branch = 'main'
    # If the current branch appears to be a feature branch, we adjust
    # all branch references to 'develop'.
    elif branch != 'main':
        branch = 'develop'

    # If a "--branch=BRANCH_NAME" argument is passed in
    # as the only positional argument, we use BRANCH_NAME.
    # Note: The --branch is required as session.posargs contains
    # the staged files passed in by pre-commit in most cases.
    if session.posargs and len(session.posargs) == 1:
        match = re.match(
            pattern=r'^--branch=([\w\.-]+)$', string=session.posargs[0].strip(),
        )
        if match:
            branch = match.groups()[0]

    rewrites = [
        {
            'name': 'github',
            'pattern': re.compile(
                fr'((((http)|(https))://github\.com/{GITHUB_REPOSITORY}/((blob)|(tree))/)([\w\.-]+)/)',  # noqa:E501
            ),
            'replacement': fr'\2{branch}/',
        },
        {
            'name': 'codecov',
            'pattern': re.compile(
                fr'((((http)|(https))://codecov.io/gh/{GITHUB_REPOSITORY}/branch/)([\w\.-]+)/)',  # noqa:E501
            ),
            'replacement': fr'\2{branch}/',
        },
    ]

    for expanded in _expand(*paths):
        with _line_by_line_replace(expanded) as (old_file, new_file):
            for line in old_file:
                for rewrite in rewrites:
                    line = re.sub(rewrite['pattern'], rewrite['replacement'], line)
                new_file.write(line)


@contextlib.contextmanager
def _line_by_line_replace(path: str) -> Generator[Tuple[IO, IO], None, None]:
    """Replace/change the lines in a file one by one.

    This generator function yields two file handles, one to the current file
    (i.e., `old_file`) and one to its replacement (i.e., `new_file`).

    Usage: loop over the lines in `old_file` and write the files to be kept
    to `new_file`. Files not written to `new_file` are removed!

    Args:
        path: the file whose lines are to be replaced

    Yields:
        old_file, new_file: handles to a file and its replacement
    """
    file_handle, new_file_path = tempfile.mkstemp()
    with os.fdopen(file_handle, 'w') as new_file:
        with open(path) as old_file:
            yield old_file, new_file

    shutil.copymode(path, new_file_path)
    os.remove(path)
    shutil.move(new_file_path, path)


@nox.session(name='format', python=MAIN_PYTHON)
def format_(session: sessions.Session) -> None:
    """Format source files with autoflake, black, and isort."""
    _begin(session)

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

    with _isort_fix(session):  # TODO (isort): remove the context manager
        session.run('isort', '--version')
        session.run('isort', *locations)


@nox.session(python=MAIN_PYTHON)
def lint(session: sessions.Session) -> None:  # noqa:WPS213
    """Lint source files with flake8, mypy, and pylint."""
    _begin(session)

    _install_packages(
        session,
        'flake8',
        'flake8-annotations',
        'flake8-black',
        'flake8-expression-complexity',
        'flake8-pytest-style',
        'mypy',
        'pylint',
        'wemake-python-styleguide',
    )

    # Interpret extra arguments as locations of source files.
    locations = session.posargs or SRC_LOCATIONS

    session.run('flake8', '--version')
    session.run('flake8', '--ignore=I0', *locations)  # TODO (isort): remove flag

    # TODO (isort): remove the entire block after upgrade is possible
    with _isort_fix(session):
        session.run('isort', '--version')
        session.run('isort', '--check-only', *locations)

    # For mypy, only lint *.py files to be packaged.
    mypy_locations = [path for path in locations if path.startswith(SRC_FOLDER)]
    if mypy_locations:
        session.run('mypy', '--version')
        session.run('mypy', *mypy_locations)
    else:
        session.log('No paths to be checked with mypy')

    # Ignore errors where pylint cannot import a third-party package due its
    # being run in an isolated environment. One way to fix this is to install
    # all develop dependencies in this nox session, which we do not do. The
    # whole point of static linting tools is to not rely on any package be
    # importable at runtime. Instead, these imports are validated implicitly
    # when the test suite is run.
    session.run('pylint', '--version')
    session.run('pylint', '--disable=import-error', *locations)


@nox.session(python=MAIN_PYTHON)
def safety(session: sessions.Session) -> None:
    """Check the dependencies for known security vulnerabilities."""
    _begin(session)

    # We do not pin the version of `safety` to always check with
    # the latest version. The risk this breaks the CI is rather low.
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
            'safety', 'check', f'--file={requirements_txt.name}', '--full-report',
        )


@nox.session(python=MAIN_PYTHON)
def docs(session: sessions.Session) -> None:
    """Build the documentation with sphinx."""
    # The latest version of the package needs to be installed
    # so that sphinx's autodoc can include the latest docstrings.
    if session.virtualenv.reuse_existing:
        raise RuntimeError('The "docs" session must be run without the "-r" option')

    _begin(session)

    # The documentation tools require the developed package.
    # Otherwise, sphinx's autodoc could not include the docstrings.
    session.run('poetry', 'install', '--no-dev', external=True)
    _install_packages(session, 'sphinx', 'sphinx-autodoc-typehints')

    session.run('sphinx-build', DOCS_SRC, DOCS_BUILD)
    # Verify all external links return 200 OK.
    session.run('sphinx-build', '-b', 'linkcheck', DOCS_SRC, DOCS_BUILD)

    print(f'Docs are available at {os.getcwd()}/{DOCS_BUILD}index.html')  # noqa:WPS421


_TEST_DEPENDENCIES = ('packaging', 'pytest', 'pytest-cov')


@nox.session(python=SUPPORTED_PYTHONS)
def test(session: sessions.Session) -> None:
    """Test the code base."""
    # Re-using an old environment is not deterministic here as
    # `poetry install --no-dev` removes previously installed packages.
    if session.virtualenv.reuse_existing:
        raise RuntimeError('The "test" session must be run without the "-r" option')

    _begin(session)

    # Install only the "lalib" package and the testing tool chain.
    session.run('poetry', 'install', '--no-dev', external=True)
    _install_packages(session, *_TEST_DEPENDENCIES)

    # Interpret extra arguments as options for pytest.
    # They are "dropped" by the hack in the test_suite() function
    # if this function is run within the "test-suite" session.
    posargs = () if session.env.get('_drop_posargs') else session.posargs

    args = posargs or (
        '--cov',
        '--no-cov-on-fail',
        '--cov-branch',
        '--cov-report=term-missing:skip-covered',
        TESTS_FOLDER,
    )

    session.run('pytest', '--version')
    session.run('pytest', *args)


@nox.session(name='test-suite', python=MAIN_PYTHON)
def test_suite(session: sessions.Session) -> None:
    """Run the entire test suite.

    Intended to be run as a pre-commit hook.

    Ignores the paths to the staged files passed in by the
    pre-commit framework and runs the entire test suite instead.
    """
    # Re-using an old environment is not deterministic here as
    # `poetry install --no-dev` removes previously installed packages.
    if session.virtualenv.reuse_existing:
        raise RuntimeError(
            'The "test-suite" session must be run without the "-r" option',
        )

    # Little hack to not work with the extra arguments provided
    # by the pre-commit framework. Create a flag in the
    # env(ironment) that must contain only `str`-like objects.
    session.env['_drop_posargs'] = 'true'

    # Cannot use session.notify() to trigger the "test" session as
    # that would create a new Session object without the flag in
    # the environment. Instead, run the test() function from here.
    test(session)


@nox.session(name='test-coverage', python=MAIN_PYTHON)
def test_coverage(session: sessions.Session) -> None:
    """Upload coverage data to Codecov.

    Intended to be run by GitHub Actions.
    """
    # Re-using an old environment is not deterministic here as
    # `poetry install --no-dev` removes previously installed packages.
    if session.virtualenv.reuse_existing:
        raise RuntimeError(
            'The "test-coverage" session must be run without the "-r" option',
        )

    _begin(session)

    # Install only the 'lalib' package and the testing tool chain.
    session.run('poetry', 'install', '--no-dev', external=True)
    _install_packages(session, 'coverage', 'codecov', *_TEST_DEPENDENCIES)

    session.run('coverage', '--version')
    session.run('coverage', 'run', '-m', 'pytest')
    session.run('coverage', 'xml', '--fail-under=0')

    session.run('codecov', '--version')
    session.run('codecov')


@nox.session(name='test-docstrings', python=MAIN_PYTHON)
def test_docstrings(session: sessions.Session) -> None:
    """Test the code examples in docstrings with xdoctest."""
    _begin(session)

    # Install only the lalib package and xdoctest.
    session.run('poetry', 'install', '--no-dev', external=True)
    _install_packages(session, 'xdoctest[optional]')

    # Interpret extra arguments as options for xdoctest.
    args = session.posargs or [PACKAGE_NAME]

    session.run('xdoctest', '--version')
    session.run('xdoctest', '--quiet', *args)  # --quiet => less verbose output


@nox.session(name='init-project', python=MAIN_PYTHON, venv_backend='none')
def init_project(session: sessions.Session) -> None:
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


@nox.session(name='clean-pwd', python=MAIN_PYTHON, venv_backend='none')
def clean_pwd(session: sessions.Session) -> None:  # noqa:WPS231
    """Remove (almost) all glob patterns listed in .gitignore.

    The difference compared to `git clean -X` is that this task
    does not remove pyenv's .python-version file and poetry's
    virtual environment.
    """
    exclude = frozenset(('.python-version', '.venv/', 'venv/'))

    with open('.gitignore') as file_handle:
        paths = file_handle.readlines()

    for path in _expand(*paths):
        if path.startswith('#'):
            continue

        for excluded in exclude:
            if path.startswith(excluded):
                break
        else:
            session.run('rm', '-rf', path)


def _expand(*patterns: str) -> Generator[str, None, None]:
    """Expand glob patterns into paths.

    Args:
        *patterns: the patterns to be expanded

    Yields:
        expanded: a single expanded path
    """  # noqa:RST213
    for pattern in patterns:
        yield from glob.glob(pattern.strip())


def _begin(session: sessions.Session) -> None:
    """Show generic info about a session."""
    if session.posargs:
        print('extra arguments:', *session.posargs)  # noqa:WPS421

    session.run('python', '--version')

    # Fake GNU's pwd.
    session.log('pwd')
    print(os.getcwd())  # noqa:WPS421


def _install_packages(
    session: sessions.Session, *packages_or_pip_args: str, **kwargs: Any,
) -> None:
    """Install packages respecting the poetry.lock file.

    This function wraps nox.sessions.Session.install() such that it installs
    packages respecting the pinnned versions specified in poetry's lock file.
    This makes nox sessions even more deterministic.

    IMPORTANT: Package installation is skipped if the `session` is run with
    the "-r" flag to re-use an existing virtual environment. That turns nox
    into a fast task runner provided that a virtual environment already exists.

    Args:
        session: the Session object
        *packages_or_pip_args: the packages to be installed or pip options
        **kwargs: passed on to nox.sessions.Session.install()
    """  # noqa:RST210,RST213
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
            external=True,
        )
        session.install(
            f'--constraint={requirements_txt.name}', *packages_or_pip_args, **kwargs,
        )


# TODO (isort): remove this block after upgrading is possible
@contextlib.contextmanager
def _isort_fix(session: sessions.Session) -> Generator:
    """Temporarily upgrade to isort 5.4.1."""
    session.install('isort==5.4.1')
    try:
        yield
    finally:
        # Go back to the version pinned in poetry.lock
        session.install('isort==4.3.21')
