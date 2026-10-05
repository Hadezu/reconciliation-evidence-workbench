# Attribution

Original project code: Copyright 2026 Ivan Matiushkin, MIT (see LICENSE). Developed with Codex. No client source code or private data is included.

Runtime dependencies are used as libraries, not represented as our implementation:

- [DuckDB](https://github.com/duckdb/duckdb), MIT, DuckDB contributors: SQL execution and local database. [Numeric type contract](https://duckdb.org/docs/current/sql/data_types/numeric).
- [openpyxl](https://openpyxl.readthedocs.io/), MIT, openpyxl contributors: XLSX parsing/writing. No Microsoft endorsement or native Excel verification implied.
- [Pydantic](https://github.com/pydantic/pydantic), MIT, Pydantic contributors: explicit rule validation.
- [defusedxml](https://github.com/tiran/defusedxml), Python Software Foundation license: XML entity-expansion protection.

Dependencies are installed from the locked registry packages. Their distribution licenses remain authoritative. No upstream repository is copied or relicensed. Development tools include pytest, Hypothesis, Ruff and Playwright; their authors and licenses remain theirs.
