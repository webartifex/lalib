"""Configure nox to run maintenance tasks in isolated environments."""

import os

import nox
from nox import sessions


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
def format_(session: sessions.Session):
    """Format the source files."""
    _info(session)


@nox.session(python=MAIN_PYTHON)
def lint(session: sessions.Session):
    """Lint the source files."""
    _info(session)


@nox.session(python=SUPPORTED_PYTHONS)
def test(session: sessions.Session):
    """Test the code base."""
    _info(session)


def _info(session: sessions.Session) -> None:
    """Show generic info about a session."""
    if session.posargs:
        print('extra arguments:', *session.posargs)

    session.run('python', '--version')

    # Fake GNU's pwd.
    session.log('pwd')
    print(os.getcwd())
