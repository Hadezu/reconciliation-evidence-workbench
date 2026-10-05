# Contract and architecture

## Input → validation → SQL → evidence

1. Read each input once into a bounded snapshot. Its hash and saved bytes refer to exactly what was parsed, even if the original file later changes.
2. Parse UTF-8 CSV with the configured delimiter, or one explicitly named XLSX sheet. Headers are exact, unique text. Unknown business columns are retained, not mapped by guesswork.
3. Normalize each tabular record, retaining source side and CSV logical-record ordinal / Excel worksheet row (header is row 1). Multiline CSV records are one logical record, not one physical line. Blank records inside the input remain invalid rows. Empty trailing space outside XLSX's actual serialized rows is not invented as data.
4. Validate before applying exclusion rules. An invalid amount on a cancelled record is still invalid, not silently hidden by cancellation.
5. Load typed rows into DuckDB in a transaction. Group by exact normalized reference and currency; do not join ambiguous raw records against each other.
6. Count source-side cardinalities. Duplicate outranks invalid; invalid outranks missing; otherwise compare the one-to-one amounts with the explicit tolerance. Excluded rows do not compete for a match but remain in the source view and separate amount buckets.
7. Independently sum eligible input amounts in Python and compare their difference with the SQL group differences, per currency. Verify row accounting.
8. Export to a private staging directory; publish the complete directory only after all writers succeed. Preserve snapshots, rules, SQL, database, report JSON/HTML/XLSX and checksums.

## Exactness and semantics

- Amount syntax: optional sign, 1–12 whole digits, up to 2 decimal digits. Decimal separator is explicit per source; thousands separators, scientific notation, NaN and extra precision are rejected. Refunds are allowed. Numeric XLSX amounts pass through their decimal representation, never binary arithmetic. More precision is not rounded into apparent agreement.
- SQL source amounts use BIGINT; aggregate sums use HUGEINT; Python uses arbitrary-size integers. JSON money fields are decimal **strings of minor units** so browser consumers do not lose values above JavaScript's safe-integer range. Browser formatting uses BigInt. XLSX money is exact decimal **text**, not a formula-based model or numeric pivot-ready financial workbook.
- Supported currency scale is exactly two for EUR/PLN/USD. Unknown currency rows remain invalid and in a separate known-amount bucket. No conversion or cross-currency grand total.
- ISO dates `YYYY-MM-DD` are reporting-date labels. ISO timestamps must contain `T` and an explicit offset; convert to UTC before testing `[period_start, period_end_exclusive)`. Naive timestamps are invalid. A native XLSX date-formatted midnight cell is a date label; a hidden nonzero time or date-time format needs explicit timezone information and is rejected.
- Numeric XLSX identifiers are rejected: leading zeros may already be lost, and a number format cannot prove their intended identity. Use text identifiers. Keys retain case; whitespace is trimmed. Currency is trimmed and uppercased; status is trimmed and matched exactly.
- One invalid group blocks its valid partner from receiving MATCH. A row with no identity cannot be attributed to a partner: it remains in source evidence and makes the whole result require review.
- Known subtotals exclude unparseable amounts; they are not full balances. Invalid rows with parseable amounts are visible in their own bucket, never included in eligible controls.
- `RECONCILED` means all in-scope comparison groups agree under the configured tolerance and no invalid rows exist. Nonzero tolerance does not erase the residual. `NO_COMPARABLE_DATA` is not a pass. Control balance is a conservation check, not evidence of business correctness.

## Failure, integrity and boundaries

Missing mapped columns, malformed CSV, oversized inputs, unsupported file types or dangerous XLSX archives fail the whole run. Row-level business errors produce a complete review report. Formulas/error cells are never evaluated or trusted as cached values. Defusedxml is installed for XML entity protection; macros and external workbook links are rejected.

Untrusted strings are written as explicit XLSX text. XML-illegal control characters are represented as visible escapes. Long raw JSON is split across cells instead of being truncated. HTML data escapes script delimiters and uses textContent, not innerHTML. The HTML is static, offline and has no input-upload endpoint or telemetry. Display is capped at 200 filtered groups/source rows; JSON/XLSX/database contain all rows.

The manifest detects changed/missing/extra files relative to its checksums. **It is not signed**, immutable or an authenticity guarantee against an attacker who can replace both files and manifest. Run fingerprints identify input bytes, file formats and engine version; they do not sign a Git commit. Repeat report JSON is deterministic; XLSX/DB binary metadata need not be byte-identical across runs/dependency versions.

Directory publication uses local same-parent rename. This is not a distributed transaction, fsync durability guarantee or network-filesystem certification. Caught failures clean their staging directory. A killed process can leave an unpublished `.recon-staging-*` directory for manual inspection/removal; no finished output is exposed. Concurrent runs to the same destination cannot replace an already published nonempty run. Local directory access is the operator's responsibility.

The output contains copies of both sources and their metadata. No encryption-at-rest, RBAC, hosted upload security or retention service is added. This is a local handover tool for trusted operators, not a public file-processing service.
