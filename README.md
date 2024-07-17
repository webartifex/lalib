# `lalib` - A Library to study Linear Algebra

The goal of this project is
    to create a library written in pure [Python](https://docs.python.org/3/)
    (incl. the [standard library](https://docs.python.org/3/library/index.html))
    and thereby learn about [linear algebra](https://en.wikipedia.org/wiki/Linear_algebra).


## Installation

The project is published on [PyPI](https://pypi.org/project/lalib/).
To install it, open any Python prompt and type:

`pip install lalib`

You may want to do so
    within a [virtual environment](https://docs.python.org/3/library/venv.html)
    or a [Jupyter notebook](https://docs.jupyter.org/en/latest/#what-is-a-notebook).


## Contributing & Development

This project is open for any kind of contribution,
    be it by writing code for new features or bugfixes
    or by raising [issues](https://github.com/webartifex/lalib/issues).


### Local Develop Environment

In order to play with the `lalib` codebase,
    you need to set up a develop environment on your own computer.

First, get your own copy of this repository:

`git clone git@github.com:webartifex/lalib.git`

While `lalib` comes without any dependencies
    except core Python and the standard library for the user,
    we assume a couple of mainstream packages be installed
    to ensure code quality during development.
These can be viewed in the [pyproject.toml](pyproject.toml) file
    and are managed with [poetry](https://python-poetry.org/docs/)
    which needs to be installed as well.
[poetry](https://python-poetry.org/docs/) also creates and manages
    [virtual environments](https://docs.python.org/3/tutorial/venv.html).

To replicate the project maintainer's develop environment exactly,
    install the *pinned* dependencies from the [poetry.lock](poetry.lock) file:

`poetry install`


### Branching Strategy

The branches in this repository follow the
    [GitFlow](https://nvie.com/posts/a-successful-git-branching-model/) model.
Feature branches must be rebased onto the "develop" branch *before* being merged.
Whereas after a rebase a simple fast-forward merge is possible,
    all merges are made with explicit and *empty* merge commits.
This ensures that past branches remain visible in the logs,
    for example, with `git log --graph`.
