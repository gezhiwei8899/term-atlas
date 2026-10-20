"""Usage: python scripts/validate.py [--examples] [--strict]."""

import argparse

from _lib import print_report, validate_repository


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--examples", action="store_true", help="also validate synthetic examples")
    parser.add_argument("--strict", action="store_true", help="treat review warnings as failures")
    args = parser.parse_args()
    report = validate_repository(args.examples)
    print_report(report)
    return int(bool(report.errors or (args.strict and report.issues)))


if __name__ == "__main__":
    raise SystemExit(main())
