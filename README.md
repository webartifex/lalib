# A Python library to study linear algebra

The goal of the `lalib` project is to create
    a library written in pure [Python](https://docs.python.org/3/)
    (incl. the [standard library](https://docs.python.org/3/library/index.html))
    and thereby learn about
        [linear algebra](https://en.wikipedia.org/wiki/Linear_algebra)
    by reading and writing code.


[![PyPI: Package version](https://img.shields.io/pypi/v/lalib?color=blue)](https://pypi.org/project/lalib/)
[![PyPI: Supported Python versions](https://img.shields.io/pypi/pyversions/lalib)](https://pypi.org/project/lalib/)
[![PyPI: Number of monthly downloads](https://img.shields.io/pypi/dm/lalib)](https://pypistats.org/packages/lalib)

[![Documentation: Status](https://readthedocs.org/projects/lalib/badge/?version=latest)](https://lalib.readthedocs.io/en/latest/?badge=latest)
[![Test suite: Status](https://github.com/webartifex/lalib/actions/workflows/tests.yml/badge.svg)](https://github.com/webartifex/lalib/actions/workflows/tests.yml)
[![Test coverage: codecov](https://codecov.io/github/webartifex/lalib/graph/badge.svg?token=J4LWOMVP0R)](https://codecov.io/github/webartifex/lalib)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type checking: mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Code linting: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)


## Installation

This project is published on [PyPI](https://pypi.org/project/lalib/).
To install it, open any Python prompt and type:

`pip install lalib`

You may want to do so
    within a [virtual environment](https://docs.python.org/3/library/venv.html)
    or a [Jupyter notebook](https://docs.jupyter.org/en/latest/#what-is-a-notebook).


## Contributing & Development

This project is open for any kind of contribution,
    be it by writing code for new features or bugfixes,
    or by raising [issues](https://github.com/webartifex/lalib/issues).
All contributions become open-source themselves, under the
    [MIT license](https://github.com/webartifex/lalib/blob/main/LICENSE.txt).


### Local Develop Environment

In order to play with the `lalib` codebase,
    you need to set up a develop environment on your own computer.

First, get your own copy of this repository:

`git clone git@github.com:webartifex/lalib.git`

While `lalib` comes without any dependencies
    except core Python and the standard library for the user,
    we assume a couple of packages and tools be installed
    to ensure code quality during development.
These can be viewed in the
    [pyproject.toml](https://github.com/webartifex/lalib/blob/main/pyproject.toml) file
    and are managed with [poetry](https://python-poetry.org/docs/)
    which needs to be installed as well.
`poetry` also creates and manages a
    [virtual environment](https://docs.python.org/3/tutorial/venv.html)
    with the develop tools,
    and pins their exact installation versions in the
    [poetry.lock](https://github.com/webartifex/lalib/blob/main/poetry.lock) file.

To replicate the project maintainer's develop environment, run:

`poetry install`


### Maintenance Tasks

We use [nox](https://nox.thea.codes/en/stable/) to run
    the test suite and other maintenance tasks during development
    in isolated environments.
`nox` is similar to the popular [tox](https://tox.readthedocs.io/en/latest/).
It is configured in the
    [noxfile.py](https://github.com/webartifex/lalib/blob/main/noxfile.py) file.
`nox` is assumed to be installed as well
    and is therefore not a project dependency.

To list all available tasks, called sessions in `nox`, simply run:

`nox --list` or `nox -l` for short

To execute all default tasks, simply invoke:

`nox`

This includes running the test suite for the project's main Python version
    (i.e., [3.12](https://devguide.python.org/versions/)).


#### Code Formatting & Linting

We follow [Google's Python style guide](https://google.github.io/styleguide/pyguide.html)
    and include [type hints](https://docs.python.org/3/library/typing.html)
    where possible.

During development,
    `nox -s format` and `nox -s lint` may be helpful.
Both can be speed up by re-using a previously created environment
    with the `-R` flag.

The first task formats all source code files with
    [autoflake](https://pypi.org/project/autoflake/),
    [black](https://pypi.org/project/black/), and
    [isort](https://pypi.org/project/isort/).

The second task lints all source code files with
    [flake8](https://pypi.org/project/flake8/),
    [mypy](https://pypi.org/project/mypy/), and
    [ruff](https://pypi.org/project/ruff/).
`flake8` is configured with a couple of plug-ins.

You may want to install the [pre-commit](https://pre-commit.com/) hooks
    that come with the project:

`nox -s pre-commit-install`

Then, the linting and testing occurs automatically before every commit.


#### Test Suite

We use [pytest](https://docs.pytest.org/en/stable/)
    to obtain confidence in the correctness of `lalib`.
To run the tests
    for *all* supported Python versions
    in isolated (and perfectly reproducable) environments,
    invoke:

`nox -s test`


### Branching Strategy

The branches in this repository follow the
    [GitFlow](https://nvie.com/posts/a-successful-git-branching-model/) model.
Feature branches are rebased onto
    the [develop](https://github.com/webartifex/lalib/tree/develop) branch
    *before* being merged.
Whereas a rebase makes a simple fast-forward merge possible,
    all merges are made with explicit and *empty* merge commits.
This ensures that past branches remain visible in the logs,
    for example, with `git log --graph`.


#### Versioning

The version identifiers adhere to a subset of the rules in
    [PEP440](https://peps.python.org/pep-0440/) and
    follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
So, releases to [PyPI](https://pypi.org/project/lalib/#history)
    come in the popular `major.minor.patch` format.
The specific rules for this project are explained
    [here](https://github.com/webartifex/lalib/blob/main/tests/test_version.py).


## Releases


### v0.4.2, 2024-09-10

- This release provides no functionality
- Its purpose is to (re-)claim the
  [lalib](https://pypi.org/project/lalib/) name on PyPI
- We can *not* start with **v0.1.0**
  because we already used this when learning to use PyPI years back
