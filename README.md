# `lalib` - A library to study linear algebra

The goal of this project is
to create a library written solely in core [Python](https://docs.python.org/3/)
    (incl. the [standard library](https://docs.python.org/3/library/index.html))
to learn about [linear algebra](https://en.wikipedia.org/wiki/Linear_algebra).

[![PyPI](https://img.shields.io/pypi/v/lalib.svg)](https://pypi.org/project/lalib/)
[![Tests](https://github.com/webartifex/lalib/workflows/Tests/badge.svg)](https://github.com/webartifex/lalib/actions?workflow=Tests)
[![Codecov](https://codecov.io/gh/webartifex/lalib/branch/main/graph/badge.svg)](https://codecov.io/gh/webartifex/lalib)


## Contributing & Development


### Local Develop Environment

Get a copy of this repository:

`git clone git@github.com:webartifex/lalib.git`

While `lalib` comes without any dependencies except core Python
    and the standard library for the user,
we assume a couple of mainstream packages to be installed
to ensure code quality during development.
These can be viewed in the [pyproject.toml](pyproject.toml) file.

To replicate the project maintainer's develop environment,
install the pinned dependencies from the [poetry.lock](poetry.lock) file
with the [poetry](https://python-poetry.org/docs/) dependency manager:

`poetry install`

This automatically creates and uses a [virtual environment](https://docs.python.org/3/tutorial/venv.html).


### Testing & Maintenance Tasks

We use [nox](https://nox.thea.codes/en/stable/) to run the test suite
    in an isolated environment
and to invoke the prepared maintenance tasks during development
(`nox` is quite similar to [tox](https://tox.readthedocs.io/en/latest/)).
It is configured in the [noxfile.py](noxfile.py) file.

To list all available tasks, called sessions in `nox`, simply run:

`poetry run nox --list`

To execute all sessions that the CI server would run, invoke:

`poetry run nox`

That runs the test suite for all supported Python versions.


#### Code Formatting & Linting

We follow [Google's Python Style Guide](https://google.github.io/styleguide/pyguide.html)
and include [type hints](https://docs.python.org/3/library/typing.html) where possible.

During development, `poetry run nox -s format` and `poetry run nox -s lint` may
    be helpful.

The first task formats all source code files with
    [autoflake](https://pypi.org/project/autoflake/),
    [black](https://pypi.org/project/black/), and
    [isort](https://pypi.org/project/isort/).
`black` keeps single quotes `'` unchanged to minimize visual noise
    (single quotes are enforced by `wemake-python-styleguide`; see next).

The second task lints all source code files with
    [flake8](https://pypi.org/project/flake8/),
    [mypy](https://pypi.org/project/mypy/), and
    [pylint](https://pypi.org/project/pylint/).
`flake8` is configured with a couple of plug-ins,
most notably [wemake-python-styleguide](https://wemake-python-stylegui.de/en/latest/).

You may want to install the local [pre-commit](https://pre-commit.com/) hooks
    that come with the project:

`poetry run nox -s init-project`

That automates the formatting and linting before every commit.
Also, the test suite is run before every merge.


### Branching Strategy

The branches in this repository follow the [GitFlow](https://nvie.com/posts/a-successful-git-branching-model/) model.
It is assumed that a feature branch is rebased *before* it is merged into `develop`.
Whereas after a rebase a simple fast-forward merge is possible,
all merges are made with explicit and *empty* merge commits
(i.e., the merge itself does *not* change a single line of code).
This ensures that past branches remain visible in the logs,
for example, with `git log --graph`.
