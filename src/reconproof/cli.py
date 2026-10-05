import argparse
import sys
from pathlib import Path

from .pipeline import run, verify


def main():
    parser = argparse.ArgumentParser(
        description="Offline CSV/XLSX reconciliation; inputs are never modified"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("run")
    for name in ("left", "right", "rules", "out"):
        build.add_argument("--" + name, type=Path, required=True)
    check = sub.add_parser("verify")
    check.add_argument("directory", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "verify":
            print("INTEGRITY_OK " + verify(args.directory))
            return 0
        report = run(args.left, args.right, args.rules, args.out)
        print(
            f"{report['verdict']} / {len(report['rows'])} rows / {args.out / 'report.html'}"
        )
        return 0 if report["verdict"] == "RECONCILED" else 2
    except Exception as error:
        print(f"FAILED: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
