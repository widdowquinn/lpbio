# `lpbio`

Scripts, tools and modules for computational biology

<!-- TOC -->

- [Development notes](#development-notes)
    - [Tests](#tests)

<!-- /TOC -->

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