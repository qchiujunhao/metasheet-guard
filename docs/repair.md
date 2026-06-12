# Repair

The repair engine applies only conservative, auditable changes by default:

- trim column names and selected values
- normalize known column aliases when no canonical column conflicts
- replace whitespace in sample IDs with underscores
- lowercase condition labels
- remove fully empty rows
- normalize FASTQ extension case

Every change is written to `changes.json`.

Suggested repairs are intentionally disabled until the project implements
auditable inference rules. Passing `--allow-suggestions` fails clearly instead
of silently applying only safe repairs.
