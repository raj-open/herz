# Developer notes #

This document contains information for developers.

## Repository ##

```text
.
├── dist
│   ├── (local only) *-{version}.zip # calling `just dist` creates this artefact
│   └── VERSION
|
├── documentation
│   ├── (generated) models/
|   |
│   └── README.md
|
├── examples
│   ├── data/
│   ├── output/
│   ├── setup
│   │   └── config.yaml
|   |
│   └── README.md
|
├── scripts/
|
├── templates/
|
├── (local only) setup/ # user should set this up, following templates/template-*.yaml
│   └── config.yaml
|
├── notebooks/
|
├── src/
|
├── tests/
|
├── justfile # contains tasks
├── pyproject.toml
├── (generated) requirements.txt
├── LICENCE
├── README.md
└── CONTRIBUTING.md
```

## System requirements and setup ##

- [Python 3.10+](https://www.python.org/downloads)
- [Justfile tool](https://github.com/casey/just#installation)
- (development only) [Node and npm](https://nodejs.org/en/download/current)

### Windows users ###

Windows users are encouraged to install **bash**.
There are a few ways to do this:

1. Install [git for windows](https://gitforwindows.org) (which includes bash).
2. [Activate ubuntu](https://devblogs.microsoft.com/commandline/bash-on-ubuntu-on-windows-download-now-3).
   This is perhaps more standard, but more complicated.

To install the **Justfile tool** you may need to install
[chocolatey](https://chocolatey.org/install)
or [scoop](https://github.com/ScoopInstaller/Scoop#installation).
And then install the tool via these
(see <https://github.com/casey/just#installation>).

### Setup ###

1. Clone the repository and ensure **git credentials** are set up.
2. Execute in a **bash** terminal

    ```bash
    just build-dev
    ```

  If the installation of python requirements throws warnings,
  run this command again.[^packages]

The 2nd step installs python packages,
generates models for the code basis,
and sets up **githooks** for QA in development.

## Git ##

### Branches and commits ###

Branch names should follow the following schemata

- `main` - reserved for (protected) main branch
- `dev` - miscellaneous development branch
- `dev-{xyz}` - development branch for feature `xyz`
- `bug-{xyz}` / `issue-{xyz}` - bugfix branch for issue `xyz`

When working in branch `B` with base `A`,
commit messages should have the format

```text
{B} > {A}: {message}
```

Before committing or pushing, ensure that
linting and testing is performed,
and that output/meta data from notebooks are wiped.
To do this run

```bash
just prettify
just tests
just clean-notebooks
```

Note that **githooks** will prevent commits containing
code which is un-linted or for which tests[^tests] fail,
or notebooks which have not been cleaned.[^notebooks]

### Merges ###

Before merging a branch, change the version number in all places:

- [dist/VERSION](dist/VERSION)
- [pyproject.toml](pyproject.toml)

etc.
(Simply search for the current version number throughout the entire repository.)
Follow the

```text
major.minor.patch
```

standard (see e.g. [this guide](https://medium.com/fiverr-engineering/major-minor-patch-a5298e2e1798)).

## The main code itself ##

The main the work is to be done in the [source](src) and [tests](tests) folders.

```text
...
├── notebooks/
│
├── src/
│   ├── thirdparty/
│   ├── core/
│   ├── models/
│   │   |
│   │   └── generated/ # generated during build process
│   │   |
│   │   ├── common.yaml # common definitions used in schemata
│   │   └── schema-*.yaml # developers define models here
|   |
│   ├── setup/
│   ├── algorithms/
│   ├── steps/
|   |
|   ├── ...
│   └── main.py # for running the code
|
├── tests/
│   ├── thirdparty/
│   ├── mockdata/
│   ├── resources/
│   ├── tests_*/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   └── tests_*.py
|   |
│   ├── conftest.py
│   └── paths.py
...
```

The entry point for the programme can be found in
the exection script [main.py](src/main.py)
and notebook [main.ipynb](notebooks/main.ipynb).
We do no want these files to be cluttered with complicated logic and calculations.
Therefore they just contain the main steps and essentially nothing else.

The repository has thus been structure, to disentangle the parts which are purely
about the structure of the programme
from the parts which are about the mathematics/science/data-analysis.
The higher the logic, the less it has to do with the maths.
In [src/steps](src/steps) data is read in, passed between the steps,
and output in the form of tables, plots, etc.
The processing steps build on methods in [src/algorithms](src/algorithms),
which contain the mathematics.

## Future ##

Here we list a few points mainly about the repository as such,
and not the code contents:

- Potential use of notebooks in the examples folder should not be entirely wiped.
  These should have their meta-data wiped, but not their outputs.
- Work with [V-lang](https://vlang.io/) instead of python?

[^packages]: In future, we may consider using virtual environments to avoid package conflicts.
[^tests]: Before commits of unit-test files, these will run by a githook.
Before pushes all tests are run.
NOTE: Before commits of source code files, no unit-tests are run,
as it is impracticable to determine the associated test file/s.
Therefore it is the responsibility of developers to run these.
