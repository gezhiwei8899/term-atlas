"""Usage: python scripts/build.py [--output dist]. Only data/ is exported."""

import argparse
from pathlib import Path

from _lib import REPO, build_dataset, print_report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=REPO / "dist")
    args = parser.parse_args()
    try:
        report = build_dataset(REPO / "data", args.output)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"build error: {exc}\n")
    print_report(report)
    if report.errors:
        return 1
    print(f"Built approved data in {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
