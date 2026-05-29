# MetaSheet-Guard

MetaSheet-Guard performs experimental-design-aware quality control for sequencing
analysis sample sheets. It targets the analysis-preparation stage: after FASTQ
generation or public metadata collection, but before running workflows such as
Nextflow, Snakemake, nf-core/rnaseq, or custom RNA-seq pipelines.

This repository currently implements the project foundation and Milestone 1:
CSV/TSV reading, bundled YAML schemas, table-structure validation, JSON reports,
and a `metasheet-guard check` command.

## Scope

MetaSheet-Guard is being built to model relationships between biological
samples, sequencing runs, lanes, FASTQ files, replicates, conditions, batches,
and downstream workflow requirements. The current release is intentionally small
and supports only the first table-level checks:

- required columns
- duplicate column names
- schema-defined column aliases
- empty values in required columns
- bundled `generic-ngs` and `bulk-rnaseq` schemas

## Non-goals

MetaSheet-Guard is not an RNA-seq aligner, quantifier, differential expression
tool, SRA downloader, nf-core/fetchngs replacement, nf-schema replacement,
Illumina BCL Convert or bcl2fastq SampleSheet validator, single-cell object
validator, spatial image validator, or generic CSV validation framework.

## Installation

```bash
pip install -e ".[dev]"
```

## Quickstart

Validate a broken bulk RNA-seq sample sheet and write a JSON report:

```bash
metasheet-guard check examples/broken/missing_required_column.csv \
  --schema bulk-rnaseq \
  --json report.json
```

The command exits with status code `1` when blocking validation errors are found.
For the example above, `report.json` contains a `REQUIRED_COLUMN_MISSING` issue
because the `bulk-rnaseq` schema requires a `condition` column.

Validate a minimal valid example:

```bash
metasheet-guard check examples/valid/bulk_rnaseq_paired.csv \
  --schema bulk-rnaseq
```

## Python API

```python
from metasheet_guard import read_sheet, validate

sheet = read_sheet("examples/broken/missing_required_column.csv")
result = validate(sheet, schema="bulk-rnaseq")

for issue in result.issues:
    print(issue.severity, issue.code, issue.message)
```

## Development

Run tests and linting:

```bash
pytest
ruff check .
```

The project uses `src/` packaging, Typer for the command-line interface, PyYAML
for schemas, pytest for tests, and Ruff for linting.
