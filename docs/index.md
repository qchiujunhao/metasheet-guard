---
hide:
  - navigation
  - toc
---

<section class="hero">
  <div class="hero__content">
    <p class="hero__eyebrow">Sequencing metadata QA before workflow execution</p>
    <h1>MetaSheet-Guard</h1>
    <p class="hero__lead">
      Experimental-design-aware quality control, auditable repair, and workflow
      export for sequencing analysis sample sheets.
    </p>
    <div class="hero__actions">
      <a class="md-button md-button--primary" href="quickstart/">Start with the quickstart</a>
      <a class="md-button" href="validators/">Explore validator rules</a>
    </div>
  </div>
  <div class="hero__visual">
    <img src="assets/images/metasheet-guard-hero.png" alt="Illustration of sequencing metadata tables, FASTQ files, and sample relationships" />
  </div>
</section>

<section class="section section--intro">
  <p class="lede">
    MetaSheet-Guard checks sequencing analysis metadata at the analysis-preparation
    stage: after FASTQ generation or public metadata collection, but before
    running downstream workflows such as Nextflow, Snakemake, nf-core/rnaseq, or
    custom RNA-seq pipelines.
  </p>
</section>

<section class="feature-grid" aria-label="Core capabilities">
  <article class="feature-card">
    <h2>Model the experiment</h2>
    <p>
      Build a canonical representation of biological samples, sequencing runs,
      lanes, FASTQ files, technical replicates, biological replicates, conditions,
      batches, and design variables.
    </p>
  </article>
  <article class="feature-card">
    <h2>Catch workflow blockers</h2>
    <p>
      Detect missing required columns, duplicate headers, empty required values,
      FASTQ path problems, paired-end mismatches, metadata conflicts, and export
      readiness issues.
    </p>
  </article>
  <article class="feature-card">
    <h2>Audit safe repairs</h2>
    <p>
      Apply conservative metadata repairs, such as alias normalization and
      whitespace cleanup, while writing a reproducible <code>changes.json</code>
      provenance record.
    </p>
  </article>
  <article class="feature-card">
    <h2>Export cleaned sheets</h2>
    <p>
      Produce canonical CSV output, nf-core/rnaseq-compatible sample sheets,
      Snakemake inputs, and DESeq2 design tables from checked metadata.
    </p>
  </article>
</section>

<section class="workflow" aria-label="MetaSheet-Guard workflow">
  <h2>Where It Fits</h2>
  <div class="workflow__steps">
    <div>
      <span>1</span>
      <p>Start with CSV, TSV, nf-core/rnaseq-style, or SRA-like metadata.</p>
    </div>
    <div>
      <span>2</span>
      <p>Validate table structure, FASTQ files, sample/run links, and design risks.</p>
    </div>
    <div>
      <span>3</span>
      <p>Repair only safe metadata issues and keep a machine-readable audit trail.</p>
    </div>
    <div>
      <span>4</span>
      <p>Export a clean sample sheet for downstream workflow execution.</p>
    </div>
  </div>
</section>

<section class="quick-command" aria-label="Quick command">
  <div>
    <p class="quick-command__label">Quickstart command</p>
    <h2>Check a dirty bulk RNA-seq sample sheet</h2>
  </div>

```bash
metasheet-guard check examples/broken/missing_required_column.csv \
  --schema bulk-rnaseq \
  --json report.json
```
</section>

<section class="signal-grid" aria-label="Example validation signals">
  <article>
    <h2>Example Issue Codes</h2>
    <ul>
      <li><code>REQUIRED_COLUMN_MISSING</code></li>
      <li><code>FASTQ_PAIR_NAME_MISMATCH</code></li>
      <li><code>SAMPLE_METADATA_CONFLICT</code></li>
      <li><code>BATCH_CONDITION_CONFOUNDED</code></li>
    </ul>
  </article>
  <article>
    <h2>Explicit Non-goals</h2>
    <p>
      MetaSheet-Guard is not an aligner, quantifier, differential-expression
      engine, SRA downloader, Illumina SampleSheet validator, or replacement for
      workflow-specific schema validators.
    </p>
  </article>
</section>
