"""Offline validation and reproducible exports for TermAtlas."""

from __future__ import annotations

import hashlib
import json
import math
import os
import tempfile
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

REPO = Path(__file__).resolve().parents[1]
LAYOUT = {
    "sensitive/zh.jsonl": ("sensitive", "zh"),
    "sensitive/en.jsonl": ("sensitive", "en"),
    "entities/people.jsonl": ("entity", "person"),
    "entities/companies.jsonl": ("entity", "company"),
    "entities/organizations.jsonl": ("entity", "organization"),
}


@dataclass(frozen=True)
class Issue:
    path: Path
    line: int
    level: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.level}: {self.message}"


@dataclass(frozen=True)
class Entry:
    path: Path
    line: int
    family: str
    record: dict[str, Any]


@dataclass
class Report:
    entries: list[Entry] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)

    @property
    def errors(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.level == "error"]

    def add(self, entry: Entry, message: str, level: str = "error") -> None:
        self.issues.append(Issue(entry.path, entry.line, level, message))


def validators(schema_dir: Path = REPO / "schemas") -> dict[str, Draft202012Validator]:
    """Resolve only bundled schemas; no network retrieval."""
    schemas = [json.loads(path.read_text("utf-8")) for path in sorted(schema_dir.glob("*.json"))]
    for schema in schemas:
        Draft202012Validator.check_schema(schema)
    registry = Registry().with_resources(
        (schema["$id"], Resource.from_contents(schema)) for schema in schemas
    )
    return {
        schema["title"]: Draft202012Validator(
            schema, registry=registry, format_checker=FormatChecker()
        )
        for schema in schemas
        if schema["title"] in {"sensitive", "entity"}
    }


def _object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number: {value}")


def read_jsonl(path: Path, family: str, report: Report) -> list[Entry]:
    entries = []
    try:
        with path.open("rb") as stream:
            for line, raw in enumerate(stream, 1):
                try:
                    text = raw.decode("utf-8")
                    if not text.strip():
                        raise ValueError("blank lines are not JSON records")
                    record = json.loads(text, object_pairs_hook=_object, parse_constant=_constant)
                    if not isinstance(record, dict):
                        raise ValueError("each line must be a JSON object")
                    entries.append(Entry(path, line, family, record))
                except (UnicodeError, ValueError, RecursionError) as exc:
                    report.issues.append(Issue(path, line, "error", f"invalid JSONL: {exc}"))
    except OSError as exc:
        report.issues.append(Issue(path, 0, "error", f"cannot read file: {exc}"))
    return entries


def exact_key(value: str) -> str:
    """Canonical equivalence only; never use this to rewrite source text."""
    return unicodedata.normalize("NFC", value)


def candidate_key(value: str) -> str:
    """Lossy candidate discovery ONLY, never an identity or export key."""
    return unicodedata.normalize("NFKC", value).casefold()


def language_base(language: str) -> str:
    return language.split("-")[0]


def labels(entry: Entry) -> list[tuple[str, str]]:
    record = entry.record
    primary = (
        [(record["language"], record["term"])]
        if entry.family == "sensitive"
        else list(record["names"].items())
    )
    return primary + [(alias["language"], alias["text"]) for alias in record["aliases"]]


def _strings(value: Any, pointer: str = ""):
    if isinstance(value, str):
        yield pointer, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield f"{pointer}/<key>", key
            yield from _strings(item, f"{pointer}/{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _strings(item, f"{pointer}/{index}")
    elif isinstance(value, float):
        # JSON also admits an overflowing exponent such as 1e999.
        if not math.isfinite(value):
            yield pointer, "\x00"


def _check_record(entry: Entry, slot: str, stage: str, report: Report) -> None:
    record = entry.record
    for pointer, text in _strings(record):
        if any(unicodedata.category(char) in {"Cc", "Cs"} for char in text):
            report.add(entry, f"{pointer}: control/surrogate characters or non-finite number")
    for language, text in labels(entry):
        if text != text.strip() or any(
            unicodedata.category(char) == "Cf" or char in "\u2028\u2029" for char in text
        ):
            report.add(entry, f"label {language}:{text!r}: whitespace/invisible format character")
    for source in record["sources"]:
        for url in [source["url"], source["rights"].get("evidence_url", source["url"])]:
            try:
                parsed = urlsplit(url)
                valid_url = (
                    parsed.scheme == "https"
                    and bool(parsed.hostname)
                    and parsed.username is None
                    and parsed.password is None
                    and not any(char.isspace() for char in url)
                    and parsed.port in {None, 443}
                )
            except ValueError:
                valid_url = False
            if not valid_url:
                report.add(entry, "source URLs must be public HTTPS URLs without credentials")
        if stage == "data" and source["rights"]["basis"] == "unresolved":
            report.add(entry, "data/ cannot contain unresolved reuse rights")
        if source["accessed_at"] > record["updated_at"]:
            report.add(entry, "source accessed_at must not be after updated_at")
    status = record["review"]["status"]
    allowed = {"data": {"approved", "deprecated"}, "pending": {"pending"}, "example": {"pending"}}
    if status not in allowed[stage]:
        report.add(entry, f"review status {status!r} is not allowed in stage {stage!r}")
    if record["created_at"] > record["updated_at"]:
        report.add(entry, "created_at must not be after updated_at")
    reviewed_at = record["review"].get("reviewed_at")
    if reviewed_at and not record["created_at"] <= reviewed_at <= record["updated_at"]:
        report.add(entry, "reviewed_at must be between created_at and updated_at")
    if entry.family == "sensitive":
        if language_base(record["language"]) != slot:
            report.add(entry, f"language does not match sensitive/{slot}.jsonl")
        regions = [region for item in record["assessments"] for region in item["regions"]]
        if len(regions) != len(set(regions)) or ("001" in regions and len(regions) != 1):
            report.add(
                entry, "assessment regions overlap; global 001 cannot have regional overrides"
            )
    elif record["entity_type"] != slot:
        report.add(entry, f"entity_type must be {slot!r} in this file")

    seen = set()
    for language, text in labels(entry):
        key = (language_base(language), exact_key(text))
        if key in seen:
            report.add(entry, f"repeated name/alias within record: {language}:{text!r}")
        seen.add(key)


def _check_duplicates(entries: list[Entry], report: Report) -> None:
    ids: dict[str, Entry] = {}
    identities: dict[tuple, Entry] = {}
    candidates: dict[tuple, dict[str, Entry]] = defaultdict(dict)
    warned: set[tuple[str, str]] = set()
    for entry in entries:
        record = entry.record
        identifier = record["id"]
        if identifier in ids:
            other = ids[identifier]
            report.add(entry, f"duplicate ID {identifier}; first at {other.path}:{other.line}")
        else:
            ids[identifier] = entry
        if entry.family == "sensitive":
            key = (
                "sensitive",
                language_base(record["language"]),
                exact_key(record["term"]),
                record["sense"],
            )
        else:
            key = (
                "entity",
                record["entity_type"],
                tuple(sorted((lang, exact_key(text)) for lang, text in record["names"].items())),
                exact_key(record["disambiguation"]),
            )
        if key in identities:
            other = identities[key]
            report.add(entry, f"duplicate entry; first at {other.path}:{other.line}")
        else:
            identities[key] = entry
        for language, text in labels(entry):
            # Never compare entity names against sensitive terms.
            candidate = (entry.family, language_base(language), candidate_key(text))
            for other_id, other in candidates[candidate].items():
                pair = tuple(sorted((identifier, other_id)))
                if identifier != other_id and pair not in warned:
                    report.add(
                        entry,
                        f"possible name/alias conflict {text!r} with {other_id} "
                        f"at {other.path}:{other.line}; review context, do not auto-merge",
                        "warning",
                    )
                    warned.add(pair)
            candidates[candidate][identifier] = entry


def validate_dataset(
    root: Path, stage: str = "data", schema_dir: Path = REPO / "schemas"
) -> Report:
    if stage not in {"data", "pending", "example"}:
        raise ValueError(f"unknown dataset stage: {stage}")
    report = Report()
    checks = validators(schema_dir)
    for path in sorted(root.rglob("*.jsonl")):
        if path.relative_to(root).as_posix() not in LAYOUT:
            report.issues.append(
                Issue(path, 0, "error", "unexpected JSONL file; extend layout first")
            )
    for relative, (family, slot) in LAYOUT.items():
        for entry in read_jsonl(root / relative, family, report):
            errors = sorted(
                checks[family].iter_errors(entry.record),
                key=lambda error: (str(list(error.absolute_path)), error.message),
            )
            for error in errors:
                pointer = "/" + "/".join(map(str, error.absolute_path))
                report.add(entry, f"schema {pointer}: {error.message}")
            if not errors:
                _check_record(entry, slot, stage, report)
                report.entries.append(entry)
    _check_duplicates(report.entries, report)
    return report


def validate_repository(include_examples: bool = False) -> Report:
    reports = [
        validate_dataset(REPO / "data"),
        validate_dataset(REPO / "pending", "pending"),
    ]
    if include_examples:
        reports.append(validate_dataset(REPO / "examples/data", "example"))
    combined = Report(
        [entry for report in reports for entry in report.entries],
        [issue for report in reports for issue in report.issues],
    )
    # A proposal with an existing ID must update/move the record, not shadow it.
    locations: dict[str, tuple[int, Entry]] = {}
    for stage_index, report in enumerate(reports):
        for entry in report.entries:
            identifier = entry.record["id"]
            if identifier in locations:
                other_stage, other = locations[identifier]
                if other_stage != stage_index:
                    combined.add(
                        entry,
                        f"ID appears in multiple stages: {identifier}; "
                        f"first at {other.path}:{other.line}",
                    )
            else:
                locations[identifier] = (stage_index, entry)
    return combined


def canonical_jsonl(records: list[dict[str, Any]]) -> str:
    return "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for record in sorted(records, key=lambda record: record["id"])
    )


def write_atomic(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    name = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            name = stream.name
            stream.write(content)
        os.replace(name, path)
    finally:
        if name and Path(name).exists():
            Path(name).unlink()


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def build_dataset(root: Path, output: Path) -> Report:
    """Validate first; emit approved records only, without touching unrelated files."""
    if output.resolve().is_relative_to(root.resolve()) or root.resolve().is_relative_to(
        output.resolve()
    ):
        raise ValueError("output and source directories must not contain one another")
    report = validate_dataset(root)
    if report.errors:
        return report
    sensitive = []
    entities = []
    words: dict[str, set[str]] = {"zh": set(), "en": set()}
    for entry in sorted(report.entries, key=lambda entry: entry.record["id"]):
        if entry.record["review"]["status"] != "approved":
            continue
        if entry.family == "sensitive":
            sensitive.append(entry.record)
            for language, text in labels(entry):
                words[language_base(language)].add(text)
        else:
            entities.append(entry.record)
    artifacts = {
        "sensitive/zh.txt": "".join(word + "\n" for word in sorted(words["zh"])).encode("utf-8"),
        "sensitive/en.txt": "".join(word + "\n" for word in sorted(words["en"])).encode("utf-8"),
        "sensitive/terms.json": _json_bytes(sensitive),
        "entities/entities.json": _json_bytes(entities),
    }
    for filename, entity_type in [
        ("people", "person"),
        ("companies", "company"),
        ("organizations", "organization"),
    ]:
        artifacts[f"entities/{filename}.json"] = _json_bytes(
            [record for record in entities if record["entity_type"] == entity_type]
        )
    artifacts["manifest.json"] = _json_bytes(
        {
            "schema_version": "1.0",
            "data_license": "CC0-1.0",
            "record_counts": {"sensitive": len(sensitive), "entities": len(entities)},
            "txt_deduplication": "exact strings; Unicode code point order; no normalization",
            "files": {
                name: hashlib.sha256(content).hexdigest()
                for name, content in sorted(artifacts.items())
            },
        }
    )
    for name, content in artifacts.items():
        write_atomic(output / name, content)
    return report


def print_report(report: Report) -> None:
    for issue in report.issues:
        print(issue)
    warnings = sum(issue.level == "warning" for issue in report.issues)
    print(
        f"{len(report.entries)} schema-valid records; "
        f"{len(report.errors)} errors; {warnings} warnings"
    )
