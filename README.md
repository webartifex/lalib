# A Python library to study linear algebra

The goal of the `lalib` project is to create
    a library written in pure [Python](https://docs.python.org/3/)
    (incl. the [standard library](https://docs.python.org/3/library/index.html))
    and thereby learn about
        [linear algebra](https://en.wikipedia.org/wiki/Linear_algebra)
    by reading and writing code.


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
