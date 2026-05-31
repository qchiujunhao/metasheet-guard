# Summary

MetaSheet-Guard is an open-source Python package and command-line tool for
quality control, auditable repair, and workflow export of sequencing analysis
sample sheets.

# Statement of Need

Sequencing analysis workflows depend on sample sheets that correctly connect
biological samples, sequencing runs, FASTQ files, replicates, conditions, and
batches. Errors at this stage can cause workflow failures or produce analyses in
which biological effects cannot be separated from technical effects.

# State of the Field

Existing tools commonly validate workflow-specific schemas or sequencing-run
sample sheets. MetaSheet-Guard targets the upstream analysis-preparation stage by
checking metadata relationships and experimental design risks before workflow
execution.

# Software Design

The package reads delimited sample sheets into a canonical table and project
model, applies schema-driven validators, records safe repair provenance, and
exports workflow-ready files.

# Functionality

Implemented functionality includes table validation, metadata checks, FASTQ
checks, sample/run/lane checks, design-risk detection, safe repair, JSON and HTML
reports, SRA RunInfo import, and workflow exporters.

# Example Use Case

The `BATCH_CONDITION_CONFOUNDED` rule detects designs where all control samples
are in one batch and all treatment samples are in another batch.

# Research Impact Statement

MetaSheet-Guard is intended to reduce preventable workflow failures and make
metadata quality-control decisions auditable before sequencing analysis begins.

# AI Usage Disclosure

Generative AI assistance was used during initial scaffolding and implementation.
Outputs are reviewed through tests, code review, and documented examples.

# Availability

The source code is available at
<https://github.com/qchiujunhao/metasheet-guard>.

# Acknowledgements

The project acknowledges the open-source bioinformatics tooling ecosystem.

# References

References are listed in `paper.bib`.
