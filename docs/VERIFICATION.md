# Verification

Implementation and evidence are under active verification on 2026-10-05. No hosted CI pass is claimed until recorded below.

Local environment: Windows, Python 3.14.4, uv 0.12.23. Exact dependency resolution in uv.lock: DuckDB 1.5.6, openpyxl 3.1.5, Pydantic 2.13.5, defusedxml 0.7.1.

The suite covers a predetermined synthetic oracle, exact arithmetic, duplicates on either side, invalid duplicates, currency isolation, timezone boundaries, missing identities, unsupported currencies, explicit tolerances, blank/malformed inputs, XLSX formulas/numeric identifiers/date cells, archive expansion, XML entity rejection, literal-string workbook output, large-integer HTML data, long workbook cell preservation, repeatability, unchanged inputs, output refusal, export failure and manifest tampering. Hypothesis additionally checks matching under input permutation and exact sums across generated cases.

Read-only browser checks of the local report confirmed exception counts, source drilldown and amount search. This caught malformed filter markup, which was corrected before publication. Automated Chromium acceptance tests and recordings are included in CI.

Not claimed: native Microsoft Excel visual inspection, PDF/OCR, external buyer acceptance, independent third-party audit, regulated financial accuracy, load/SLA benchmark, public server security, client production deployment or modification of work.matiushkin.com.
