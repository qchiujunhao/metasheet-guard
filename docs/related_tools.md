# Related Tools

MetaSheet-Guard complements workflow-specific validators instead of replacing
them.

`nf-schema` validates pipeline parameter and sample-sheet schemas for nf-core
workflows. MetaSheet-Guard focuses earlier on metadata quality, repair
provenance, and experimental design risks.

`nf-core/fetchngs` fetches public sequencing data and creates workflow inputs.
MetaSheet-Guard does not download data.

Illumina SampleSheet validators such as Samshee target sequencing-run sample
sheets. MetaSheet-Guard targets analysis-preparation metadata after FASTQ
generation or public metadata collection.

Frictionless and generic table validators validate general tabular structure.
MetaSheet-Guard adds sequencing-specific relationships between samples, runs,
FASTQ files, replicates, conditions, and batches.

ISA-tools and metadata standards provide rich metadata representation.
MetaSheet-Guard is a lightweight workflow-preparation checker and exporter.
