"""Publish a complete evidence directory atomically. Inputs are snapshots, never edited."""

import json
import shutil
import tempfile
from pathlib import Path

from . import __version__
from .engine import SQL, calculate
from .export import dump_json, html_report, portable, sha, workbook
from .ingest import MAX_BYTES, normalize
from .rules import load_rules


def bounded_read(path, limit):
    with Path(path).open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError(f"Input larger than {limit} bytes")
    return data


def run(left: Path, right: Path, rules_path: Path, output: Path):
    output = Path(output).absolute()
    if output.exists():
        raise ValueError("Output already exists; choose a new run directory")
    snapshots = {
        "left": bounded_read(left, MAX_BYTES),
        "right": bounded_read(right, MAX_BYTES),
        "rules": bounded_read(rules_path, 64_000),
    }
    rules = load_rules(snapshots["rules"])
    rows = normalize(snapshots["left"], left.suffix.lower(), "left", rules) + normalize(
        snapshots["right"], right.suffix.lower(), "right", rules
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".recon-staging-", dir=output.parent))
    try:
        source_names = {
            "left": "left" + left.suffix.lower(),
            "right": "right" + right.suffix.lower(),
            "rules": "rules.json",
        }
        (stage / "inputs").mkdir()
        for side, data in snapshots.items():
            (stage / "inputs" / source_names[side]).write_bytes(data)
        report = calculate(rows, rules, stage / "evidence.duckdb")
        report["provenance"] = {
            side: {"file": "inputs/" + source_names[side], "sha256": sha(data)}
            for side, data in snapshots.items()
        }
        report["engine_version"] = __version__
        report["run_key"] = sha(
            dump_json({"engine": __version__, "inputs": report["provenance"]}).encode()
        )
        (stage / "report.json").write_text(
            dump_json(portable(report)), encoding="utf-8"
        )
        (stage / "query.sql").write_text(SQL, encoding="utf-8")
        workbook(report, stage / "reconciliation.xlsx")
        html_report(report, stage / "report.html")
        manifest = {
            "schema_version": 1,
            "run_key": report["run_key"],
            "files": {
                path.relative_to(stage).as_posix(): sha(path.read_bytes())
                for path in sorted(stage.rglob("*"))
                if path.is_file()
            },
        }
        (stage / "manifest.json").write_text(dump_json(manifest), encoding="utf-8")
        # Destination must not exist. Same-parent rename gives atomic visibility on local filesystems.
        if output.exists():
            raise ValueError("Output was created by another process")
        stage.rename(output)
        return report
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def verify(directory: Path):
    directory = Path(directory).resolve()
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or not isinstance(
        manifest.get("files"), dict
    ):
        raise ValueError("Invalid manifest")
    expected = manifest["files"]
    actual = {
        p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()
    } - {"manifest.json"}
    if actual != set(expected):
        raise ValueError("Missing or unexpected evidence files")
    for name, digest in expected.items():
        target = directory / name
        if (
            target.is_symlink()
            or not target.resolve().is_relative_to(directory)
            or sha(target.read_bytes()) != digest
        ):
            raise ValueError("Evidence integrity mismatch: " + name)
    return manifest["run_key"]
