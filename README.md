# `lpbio`

Scripts, tools and modules for computational biology

<!-- TOC -->

- [Scripts](#scripts)
- [Modules](#modules)
- [Development notes](#development-notes)
    - [Tests](#tests)

<!-- /TOC -->

## Scripts

When installed, the `lpbio` package provides the following scripts, available at the command-line:

- `bulk_prokka`: for application of `prokka` [https://github.com/tseemann/prokka](https://github.com/tseemann/prokka) to a directory of input bacterial genome assemblies, taking advantage of local schedulers.

## Modules

The `lpbio` package provides the following modules for use in Python applications and scripts

- `pysge`: a module that writes job files compatible with SGE-like schedulers, and runs them.

## Development notes

Create a local environment, e.g. in `conda`, and install with `pip install -e .`:

```bash
$ conda create --name lpbio
$ source activate lpbio
$ pip install -e .
```

### Tests

Tests are intended to be run with `pytest` from the repository root:

```bash
$ pwd
lpbio/
$ pytest
```