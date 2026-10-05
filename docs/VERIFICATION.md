# Verification

Checked 2026-10-05. Implementation revision: `89e3c8703d8986cc61b4bf35181a1eda2059c535`. Later documentation/media-only commits do not change it.

- **Local Windows: 69 tests passed**, including 35 generated Hypothesis cases inside one property test. Ruff lint/format and wheel/source build passed.
- **Hosted Windows/Python 3.14: PASS** on [run 37373593062](https://github.com/Hadezu/reconciliation-evidence-workbench/actions/runs/37373593062). This is the actual implementation revision, not an earlier proxy.
- **Local Windows/Chromium: PASS**, `python -m pytest browser_checks -q --junitxml=test-results/local-browser.xml`: 1 end-to-end scenario passed in 12.30 seconds on the same implementation. It checks duplicate source evidence, amount search, outcome filters, all 25 source rows, Escape dismissal, a 390px viewport without page overflow, no JavaScript errors and no HTTP(S) requests. Screenshots were visually inspected; the actual interaction recording is included in the release.
- **Hosted Linux/Chromium on that revision: queued at the last readback.** GitHub reported an [Actions runner-assignment incident](https://www.githubstatus.com/incidents/3q1yb5m7ltvb). Do not treat a queued workflow or successful Windows job as full matrix/browser success. Consult the run for subsequent provider state.
- Earlier Linux execution passed the initial core suite/build and exercised source drilldown, search and screenshots; it found an accessible-label issue at the filter. The fix is committed. Earlier Windows execution found an implicit text-encoding assumption in a test; explicit UTF-8 fixed it.
- A built wheel was installed into an isolated environment and generated the expected complete review report; its evidence manifest verified. The final implementation change after that smoke only prevents annotation of extra CSV cells from overwriting an identically named original column; it has a targeted regression test and is included in the 69-test suite.
- Synthetic handover output has 25 retained rows, 8 exception groups and independently checked currency totals. Manifest verification passed. Outputs are complete even though their honest business verdict is `REVIEW_REQUIRED`.

Local environment: Windows, Python 3.14.4, uv 0.12.23. Exact dependency resolution in uv.lock: DuckDB 1.5.6, openpyxl 3.1.5, Pydantic 2.13.5, defusedxml 0.7.1.

The suite covers a predetermined synthetic oracle, exact arithmetic, duplicates on either side, invalid duplicates, currency isolation, timezone boundaries, missing identities, unsupported currencies, explicit tolerances, blank/malformed inputs, XLSX formulas/numeric identifiers/date cells, archive expansion, XML entity rejection, literal-string workbook output, large-integer HTML data, long workbook cell preservation, repeatability, unchanged inputs, output refusal, export failure and manifest tampering. Hypothesis additionally checks matching under input permutation and exact sums across generated cases.

Earlier read-only browser checks caught malformed filter markup, which was corrected before publication. The complete local automated Chromium scenario subsequently passed. CI also contains that scenario; its queued Linux execution is still a separate pending check.

The published v0.1.0 release has a verified Windows reference environment, including Chromium. Pending hosted Linux verification is disclosed rather than represented as a passing cross-platform matrix. The release tag preserves the tested implementation; subsequent documentation/media commits on main record the final local evidence. No application code changed during this final verification pass.

To repeat browser acceptance locally after `uv sync --locked`:

```sh
uv run playwright install chromium
uv run pytest browser_checks -q --junitxml=test-results/browser.xml
```

On Linux, `uv run playwright install --with-deps chromium` also installs the browser's system dependencies. This test creates a temporary synthetic report and opens it in an isolated Chromium instance; it does not use a personal browser profile.

The regression suite also covers actual separate-process death before publication and competing output writers. A killed run leaves unpublished staging data for inspection; caught errors clean their staging directory. Neither is called a completed report. Unit/readback checks inspect workbook values, cell types and raw-data preservation; no native Excel rendering claim is made.

Not claimed: native Microsoft Excel visual inspection, PDF/OCR, external buyer acceptance, independent third-party audit, regulated financial accuracy, load/SLA benchmark, public server security, client production deployment or modification of work.matiushkin.com.
