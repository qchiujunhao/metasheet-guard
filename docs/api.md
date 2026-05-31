# Python API

```python
from metasheet_guard import export_sheet, read_sheet, repair_sheet, validate

sheet = read_sheet("examples/valid/bulk_rnaseq_paired.csv")
result = validate(sheet, schema="bulk-rnaseq")
fixed = repair_sheet(sheet, schema="bulk-rnaseq")
export_sheet(sheet, target="nf-core-rnaseq", output="nfcore_samplesheet.csv")
```
