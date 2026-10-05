"""Inspectable SQL reconciliation. No fuzzy joins, first-match wins, or cross-currency totals."""

import json

import duckdb

from .rules import Rules

SQL = """
WITH groups AS (
  SELECT key, currency,
    count(*) FILTER (WHERE side='left') AS left_count,
    count(*) FILTER (WHERE side='right') AS right_count,
    count(*) FILTER (WHERE disposition='invalid') AS invalid_count,
    coalesce(sum(amount_minor) FILTER (WHERE side='left' AND disposition='eligible'),0)::HUGEINT AS left_minor,
    coalesce(sum(amount_minor) FILTER (WHERE side='right' AND disposition='eligible'),0)::HUGEINT AS right_minor,
    list(source_row ORDER BY source_row) FILTER (WHERE side='left') AS left_rows,
    list(source_row ORDER BY source_row) FILTER (WHERE side='right') AS right_rows
  FROM source_rows WHERE disposition<>'excluded' AND key<>'' GROUP BY key,currency
)
SELECT *, (left_minor-right_minor)::HUGEINT AS known_delta_minor,
  CASE WHEN left_count>1 OR right_count>1 THEN 'AMBIGUOUS_DUPLICATE'
       WHEN invalid_count>0 THEN 'INVALID_GROUP'
       WHEN left_count=0 THEN 'RIGHT_ONLY'
       WHEN right_count=0 THEN 'LEFT_ONLY'
       WHEN left_minor=right_minor THEN 'MATCH'
       WHEN abs(left_minor-right_minor)<=? THEN 'WITHIN_TOLERANCE'
       ELSE 'AMOUNT_MISMATCH' END AS status
FROM groups ORDER BY currency,key
"""


def as_dicts(cursor):
    names = [x[0] for x in cursor.description]
    return [dict(zip(names, row, strict=True)) for row in cursor.fetchall()]


def calculate(rows: list[dict], rules: Rules, db_path):
    with duckdb.connect(
        str(db_path), config={"enable_external_access": "false", "threads": "1"}
    ) as db:
        db.execute("BEGIN")
        db.execute("""CREATE TABLE source_rows(side VARCHAR, source_row INTEGER, key VARCHAR, currency VARCHAR,
          amount_minor BIGINT, report_date VARCHAR, disposition VARCHAR, reason VARCHAR, raw_json VARCHAR,
          PRIMARY KEY(side,source_row))""")
        if rows:
            db.executemany(
                "INSERT INTO source_rows VALUES (?,?,?,?,?,?,?,?,?)",
                [list(row.values()) for row in rows],
            )
        db.execute("CREATE TABLE rules(json VARCHAR)")
        db.execute("INSERT INTO rules VALUES (?)", [rules.model_dump_json()])
        db.execute("CREATE TABLE reconciliation AS " + SQL, [rules.tolerance_minor])
        results = as_dicts(
            db.execute("SELECT * FROM reconciliation ORDER BY currency,key")
        )
        totals = as_dicts(
            db.execute("""SELECT side,currency,disposition,count(*) AS rows,
          count(amount_minor) AS rows_with_amount,coalesce(sum(amount_minor),0)::HUGEINT AS known_minor
          FROM source_rows GROUP BY side,currency,disposition ORDER BY side,currency,disposition""")
        )
        accounting = as_dicts(
            db.execute("""SELECT side,count(*) AS source_rows,
          count(*) FILTER(WHERE disposition='eligible') AS eligible,
          count(*) FILTER(WHERE disposition='invalid') AS invalid,
          count(*) FILTER(WHERE disposition='excluded') AS excluded
          FROM source_rows GROUP BY side ORDER BY side""")
        )
        # Independent control: all eligible input amounts must appear once in grouped results.
        bridges = []
        for currency in rules.currencies:
            left, right = [
                sum(
                    r["amount_minor"]
                    for r in rows
                    if r["side"] == side
                    and r["currency"] == currency
                    and r["disposition"] == "eligible"
                )
                for side in ("left", "right")
            ]
            grouped = sum(
                r["known_delta_minor"] for r in results if r["currency"] == currency
            )
            if left - right != grouped:
                raise RuntimeError("Reconciliation control failed")
            bridges.append(
                {
                    "currency": currency,
                    "left_eligible_minor": left,
                    "right_eligible_minor": right,
                    "difference_minor": left - right,
                    "grouped_difference_minor": grouped,
                    "balanced": True,
                }
            )
        if sum(x["source_rows"] for x in accounting) != len(rows):
            raise RuntimeError("Row accounting failed")
        has_invalid = any(r["disposition"] == "invalid" for r in rows)
        exceptions = sum(
            r["status"] not in {"MATCH", "WITHIN_TOLERANCE"} for r in results
        )
        verdict = "REVIEW_REQUIRED" if has_invalid or exceptions else "RECONCILED"
        if not has_invalid and not any(r["disposition"] == "eligible" for r in rows):
            verdict = "NO_COMPARABLE_DATA"
        report = {
            "verdict": verdict,
            "exception_groups": exceptions,
            "rules": rules.model_dump(),
            "row_accounting": accounting,
            "totals": totals,
            "bridges": bridges,
            "results": results,
            "rows": rows,
        }
        db.execute("CREATE TABLE summary(json VARCHAR)")
        db.execute(
            "INSERT INTO summary VALUES (?)",
            [
                json.dumps(
                    {k: v for k, v in report.items() if k not in {"rows", "results"}}
                )
            ],
        )
        db.execute("COMMIT")
    return report
