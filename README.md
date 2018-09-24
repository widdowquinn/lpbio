# `lpbio`

Scripts, tools and modules for computational biology

<!-- TOC -->

- [`lpbio`](#lpbio)
    - [Scripts](#scripts)
    - [Modules](#modules)
    - [Development notes](#development-notes)
        - [Tests](#tests)

<!-- /TOC -->

## Scripts

When installed, the `lpbio` package provides the following scripts, available at the command-line:

- `bulk_prokka`: for application of [`prokka`](https://github.com/tseemann/prokka) to a directory of input bacterial genome assemblies, taking advantage of local schedulers.

## Modules

The `lpbio` package provides the following modules for use in Python applications and scripts

- `pysge`: a module that writes job files compatible with SGE-like schedulers, and runs them.
- `swarm`: a module for interacting with the [`Swarm`](https://github.com/torognes/swarm) clustering tool and its output.

## Development notes

Create a local environment, e.g. in `conda`, and install with `pip install -e .`:

```bash
$ conda create --name lpbio
$ source activate lpbio
$ pip install -e .
```

### Tests

Tests are intended to be run with `pytest` from the repository root (coverage can be measured using `coverage` and `pytest-cov`):

```bash
$ pwd
lpbio/
$ pytest --cov
```