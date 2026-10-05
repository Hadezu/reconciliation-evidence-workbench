# From a browser scenario to a file-based reconciliation handover

## Service and buyer evidence checked 2026-10-05

The live [portfolio homepage](https://work.matiushkin.com/en?task=reporting) offers an explanation of disagreeing reports. Its [Revenue BI page](https://work.matiushkin.com/en/proof/revenue-bi) demonstrates source tracing, exclusions and overlap reconciliation using a representative synthetic model. That is the service this project strengthens.

Two buyer-authored requirement sources informed the work:

1. [Independent QA Challenge — Python Financial Reconciliation Tool](https://www.upwork.com/freelance-jobs/apply/Independent-Challenge-Python-Financial-Reconciliation-Tool_~022097484394899912997/), posted September 2026, inspected 2026-10-05. It asks for an independently prepared adversarial synthetic dataset, predetermined answers, duplicates/ambiguity, malformed inputs, timezone conditions, row preservation and inspectable workbook outputs. It is a review assignment, not a request to build this tool. Its US-only location restriction and native Excel requirement mean it is **not presented as our eligible lead**.
2. [Weekly Excel Data Reconciliation & QA Specialist](https://www.upwork.com/freelance-jobs/apply/Weekly-Excel-Data-Reconciliation-Specialist_~022104333107026349304/), page said posted last week when inspected 2026-10-05. It calls for finding discrepancies, safe duplicate handling, source-to-summary validation and checking generated Excel results. Its screenshot/ChatGPT extraction and master-workbook editing scope extends beyond this project.

These are evidence of requested mechanisms, not a statistical market ranking, client history, proof of present hiring availability or permission to contact anyone. Seller service listings were excluded from buyer evidence. No applications were submitted.

## The gap we filled

The portfolio repository already contains reconciliation calculations and browser demonstrations. Atomic CRM adds contact-import review; the Java project covers a maintenance defect; the FastAPI project covers durable webhook recovery. Repeating those would add little.

This project accepts separately shaped real file formats, makes mapping/date/amount policy explicit, runs an inspectable SQL comparison and produces a portable evidence package with original snapshots and checksums. The sample remains synthetic, but the parser/pipeline are executable against another bounded export under the documented contract.

No existing application needed to be forked: this problem is a local batch analytical tool. DuckDB and openpyxl are attributed dependencies; our contribution is the contract, ingestion, comparison, independent controls, export, tests and handover.

## Acceptance criteria and hand-calculated example

- Preserve 14 left and 11 right records: 25 total.
- Left: 9 eligible, 3 invalid, 2 excluded. Right: 9 eligible, 0 invalid, 2 excluded.
- Eligible EUR left: `100 + 250.10 + 40 + 20 + 30 + 9 - 15 = 434.10`.
- Eligible EUR right: `100 + 249 + 50 + 11 + 9 - 15 + 30 + 7 = 441.00`.
- EUR difference: `434.10 - 441.00 = -6.90`; PLN: `120 - 121 = -1`; USD: `10 - 0 = 10`. Never add those currencies together.
- Three matched groups and eight exception groups. A missing-key invalid row is visible but cannot form an identity group.
- `INV-004` is ambiguous, even though `20 + 30 = 50`; no invented consolidation rule.
- Timestamp `2026-10-01T00:30:00+02:00` belongs to September UTC, while `2026-09-01T00:30:00+02:00` does not.
- Same snapshots/rules/version produce the same report JSON and run fingerprint. Sources remain unchanged.
- A handled export failure publishes no output; a tampered artifact fails checksum verification.

`examples/expected.json` was written before the first engine test; counts were checked by hand against the fixture. The test oracle does not import or reuse the matching algorithm. It is authored by the same project author, not an independent third-party audit.

## Review decisions

A zero aggregate difference can conceal ambiguity. We deliberately expose duplicates instead of using a convenient first match or automatic sum. Explicit grouping prevents many-to-many multiplication.

The XLSX is an immutable review snapshot with exact text amounts. A buyer who needs editable Excel formulas, pivots, template preservation or native Excel verification needs a separately agreed extension; none is implied by generating XLSX.

Codex assisted implementation and tests. Review identified potential JavaScript precision loss, XLSX cell truncation and hidden Excel date times before publication; the implementation and targeted tests address them. The XML-entity test initially expected the inner exception rather than openpyxl's wrapping exception; the test now verifies the underlying entity rejection. No measured AI speed/cost advantage is claimed.
