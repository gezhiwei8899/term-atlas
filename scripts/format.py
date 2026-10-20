"""Sort JSONL records/keys without changing strings, IDs, aliases or arrays."""

import argparse

from _lib import LAYOUT, REPO, canonical_jsonl, print_report, validate_repository, write_atomic


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="report changes without writing")
    args = parser.parse_args()
    report = validate_repository(include_examples=True)
    if report.errors:
        print_report(report)
        return 1
    changed = False
    for root in [REPO / "data", REPO / "pending", REPO / "examples/data"]:
        for relative in LAYOUT:
            path = root / relative
            content = canonical_jsonl(
                [entry.record for entry in report.entries if entry.path == path]
            ).encode("utf-8")
            if path.read_bytes() != content:
                changed = True
                print(f"{'Would format' if args.check else 'Formatting'} {path}")
                if not args.check:
                    write_atomic(path, content)
    return int(args.check and changed)


if __name__ == "__main__":
    raise SystemExit(main())
