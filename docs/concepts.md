# Concepts

A biological sample is the biological material being compared in the study.

A sequencing run is a technical sequencing event for a sample. A sample can have
multiple runs or lanes.

A lane is a subdivision of a sequencing flow cell. Lanes should usually be
represented as technical runs, not as separate biological samples.

A technical replicate is repeated technical measurement of the same biological
sample. A biological replicate is an independent biological unit in the same
condition.

A condition is the primary biological group or treatment. A batch is a technical
or processing variable that can affect measurements.

Confounding occurs when a biological condition cannot be separated from another
variable, such as all controls appearing in batch1 and all treatments appearing
in batch2.

A canonical sample sheet is a normalized representation with stable columns for
samples, conditions, runs, FASTQ files, and workflow export fields.
