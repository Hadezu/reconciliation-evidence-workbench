# From conflicting exports to an explainable review package

## Business problem

Two exports can disagree because of duplicates, mapping differences or ambiguous matches. A total alone does not explain which source rows caused the difference.

## Implemented solution

Implemented separately mapped CSV/XLSX ingestion, exact-money comparison, ambiguous-match isolation and row provenance, packaged as an interactive HTML report, an XLSX workbook and inspectable DuckDB evidence.

## Inspect the result

The downloadable synthetic example includes source snapshots and checksums. Reproduction instructions and failure checks let a technical reviewer follow the comparison from input rows to reported differences.

[Implementation and demonstration](../README.md) · [Recorded verification](VERIFICATION.md)

## Apply this to your business

The same mechanisms can support a new application, an integration or an improvement to your existing system. Scope and acceptance checks are agreed around your workflow. **[Discuss your project](https://work.matiushkin.com/en/contact)**.

[Requirement research and project context](REQUIREMENT-RESEARCH.md) · [Verification scope](../PRESENTATION-SCOPE.md)
