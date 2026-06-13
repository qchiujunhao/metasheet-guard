# Quickstart

Install MetaSheet-Guard from PyPI:

```bash
python -m pip install metasheet-guard
```

The commands below use files from the repository `examples/` directory. Run them
from a source checkout, or replace the paths with your own sample sheet.

Check a bulk RNA-seq sample sheet:

```bash
metasheet-guard check examples/valid/bulk_rnaseq_paired.csv \
  --schema bulk-rnaseq \
  --json report.json \
  --html report.html
```

Repair safe metadata issues:

```bash
metasheet-guard repair examples/broken/condition_case_mixed.csv \
  --schema bulk-rnaseq \
  --out clean.csv \
  --changes changes.json
```

Export for nf-core/rnaseq:

```bash
metasheet-guard export clean.csv \
  --target nf-core-rnaseq \
  --out nfcore_samplesheet.csv
```
