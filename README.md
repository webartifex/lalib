# A library to study Linear Algebra

The goal of this project is
to create a library written solely in core [Python](https://docs.python.org/3/)
    (incl. the [standard library](https://docs.python.org/3/library/index.html))
to learn about [linear algebra](https://en.wikipedia.org/wiki/Linear_algebra).


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

This automatically creates and uses a
    [virtual environment](https://docs.python.org/3/tutorial/venv.html).


### Testing & Maintenance Tasks

We use [nox](https://nox.thea.codes/en/stable/) to run
the test suite and the maintenance tasks during development
in isolated environments
(`nox` is quite similar to [tox](https://tox.readthedocs.io/en/latest/)).
It is configured in the [noxfile.py](noxfile.py) file.

To list all available tasks, called sessions in `nox`, simply run:

`poetry run nox --list`

To execute all sessions that the CI server would run, invoke:

`poetry run nox`

During development, `poetry run nox -s format` and `poetry run nox -s lint` may
    be helpful.
Both re-use a previous environment with the `-r` flag.


### Branching Strategy

The branches in this repository follow the
    [GitFlow](https://nvie.com/posts/a-successful-git-branching-model/) model.
It is assumed that a feature branch is rebased *before* it is merged into `develop`.
Whereas after a rebase a simple fast-forward merge is possible,
all merges are made with explicit and *empty* merge commits
(i.e., the merge itself does *not* change a single line of code).
This ensures that past branches remain visible in the logs,
for example, with `git log --graph`.
