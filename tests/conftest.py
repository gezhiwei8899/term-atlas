"""All records created by these fixtures are synthetic, including approved ones."""

import copy
import json
from pathlib import Path

import pytest

from scripts._lib import LAYOUT, REPO


@pytest.fixture
def dataset(tmp_path):
    root = tmp_path / "data"
    for name in LAYOUT:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    return root


@pytest.fixture
def term():
    record = json.loads((REPO / "examples/data/sensitive/zh.jsonl").read_text("utf-8"))
    record["review"] = {
        "status": "approved",
        "reviewed_by": "synthetic-test-reviewer",
        "reviewed_at": "2026-10-20",
        "note": "Test fixture, not a human-reviewed production record.",
    }
    record["sources"][0]["rights"] = {
        "basis": "fact_reference",
        "note": "Synthetic source metadata for testing; never production data.",
    }
    return copy.deepcopy(record)


@pytest.fixture
def entity(term):
    record = json.loads((REPO / "examples/data/entities/companies.jsonl").read_text("utf-8"))
    record["review"] = copy.deepcopy(term["review"])
    record["sources"] = copy.deepcopy(term["sources"])
    return record


@pytest.fixture
def write():
    def write_records(root: Path, relative: str, *records):
        path = root / relative
        path.write_text(
            "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
            encoding="utf-8",
        )
        return path

    return write_records
