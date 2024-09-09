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
