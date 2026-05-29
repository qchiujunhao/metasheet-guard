# Contributing

MetaSheet-Guard welcomes contributions that improve sequencing analysis
metadata quality control, documentation, tests, and examples.

## Development setup

```bash
pip install -e ".[dev]"
pytest
ruff check .
```

## Contribution guidelines

- Keep changes focused on one behavior or documentation topic.
- Add tests for new validators, report fields, schemas, and CLI behavior.
- Use stable issue codes for validation rules.
- Do not add assay scopes that are outside the current roadmap without opening
  a design discussion first.
- Public documentation should be understandable without access to project chat
  history or private planning notes.

## Reporting issues

When reporting a validator problem, include a minimal sample sheet, the schema
used, the command run, the observed issue code or output, and the expected
behavior.
