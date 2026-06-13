# Installation

MetaSheet-Guard is published on PyPI as `metasheet-guard` and requires
Python 3.10 or newer.

## Install From PyPI

Install into your current Python environment:

```bash
python -m pip install metasheet-guard
```

Verify the command-line tool is available:

```bash
metasheet-guard --version
```

## Isolated CLI Install

If you mainly want the `metasheet-guard` command, `pipx` keeps the tool isolated
from your project environments:

```bash
pipx install metasheet-guard
metasheet-guard --version
```

Upgrade an existing `pipx` install with:

```bash
pipx upgrade metasheet-guard
```

## Virtual Environment Install

For reproducible project work, create a virtual environment first:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install metasheet-guard
```

On Windows PowerShell, activate the environment with:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Upgrade

```bash
python -m pip install --upgrade metasheet-guard
```

## Development Install

Use an editable install only when contributing to the repository or running the
checked-in examples and tests:

```bash
git clone https://github.com/qchiujunhao/metasheet-guard.git
cd metasheet-guard
python -m pip install -e ".[dev]"
pytest
```

The PyPI wheel installs the Python package and CLI. The repository contains
additional development files, examples, tests, documentation sources, and paper
drafts.
