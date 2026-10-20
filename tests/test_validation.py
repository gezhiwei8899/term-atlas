import copy
import json

import pytest

from scripts._lib import REPO, candidate_key, exact_key, validate_dataset, validate_repository


def messages(report):
    return "\n".join(str(issue) for issue in report.issues)


def test_valid_bilingual_data(dataset, term, entity, write):
    write(dataset, "sensitive/zh.jsonl", term)
    en = copy.deepcopy(term)
    en.update(
        id="st_d4d4c421-158f-402e-8364-14bbdb2b7fb9",
        term="test-only placeholder",
        language="en",
        aliases=[],
    )
    write(dataset, "sensitive/en.jsonl", en)
    write(dataset, "entities/companies.jsonl", entity)
    report = validate_dataset(dataset)
    assert not report.issues
    assert len(report.entries) == 3


@pytest.mark.parametrize(
    "raw",
    [
        b"{broken}\n",
        b'{"term":"x","term":"y"}\n',
        b'{"nested":{"x":1,"x":2}}\n',
        b'{"number":NaN}\n',
        b'{"number":Infinity}\n',
        b"[]\n",
        b"\n",
        b"\xff\n",
        b"\xef\xbb\xbf{}\n",
        b"{} {}\n",
    ],
)
def test_invalid_jsonl_has_file_and_line(dataset, raw):
    path = dataset / "sensitive/zh.jsonl"
    path.write_bytes(b"{}\n" + raw)
    report = validate_dataset(dataset)
    assert any(issue.path == path and issue.line == 2 for issue in report.errors)
    assert "invalid JSONL" in messages(report)


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("term", 123),
        ("term", ""),
        ("term", " "),
        ("language", "zz"),
        ("language", "EN"),
        ("id", "name-derived"),
        ("schema_version", "2.0"),
        ("created_at", "2026-02-30"),
        ("updated_at", None),
        ("unknown_field", True),
        ("extensions", {"not_namespaced": "x"}),
    ],
)
def test_schema_types_and_formats(dataset, term, write, key, value):
    term[key] = value
    write(dataset, "sensitive/zh.jsonl", term)
    assert "schema" in messages(validate_dataset(dataset))


def test_missing_required_field(dataset, term, write):
    del term["sources"]
    write(dataset, "sensitive/zh.jsonl", term)
    assert "'sources' is a required property" in messages(validate_dataset(dataset))


def test_duplicate_id_and_entry(dataset, term, write):
    write(dataset, "sensitive/zh.jsonl", term, term)
    result = messages(validate_dataset(dataset))
    assert "duplicate ID" in result
    assert "duplicate entry" in result


def test_duplicate_entry_with_different_id(dataset, term, write):
    other = copy.deepcopy(term)
    other["id"] = "st_d4d4c421-158f-402e-8364-14bbdb2b7fb9"
    write(dataset, "sensitive/zh.jsonl", term, other)
    assert "duplicate entry" in messages(validate_dataset(dataset))


def test_nfc_equivalent_spelling_is_duplicate(dataset, term, write):
    term.update(term="café", language="en", aliases=[])
    other = copy.deepcopy(term)
    other.update(id="st_d4d4c421-158f-402e-8364-14bbdb2b7fb9", term="cafe\u0301")
    write(dataset, "sensitive/en.jsonl", term, other)
    assert "duplicate entry" in messages(validate_dataset(dataset))


@pytest.mark.parametrize(("first", "second"), [("ABC", "ＡＢＣ"), ("Test", "test"), ("①", "1")])
def test_compatibility_and_case_are_warning_only(dataset, term, write, first, second):
    term.update(term=first, language="en", aliases=[])
    other = copy.deepcopy(term)
    other.update(id="st_d4d4c421-158f-402e-8364-14bbdb2b7fb9", term=second)
    write(dataset, "sensitive/en.jsonl", term, other)
    report = validate_dataset(dataset)
    assert not report.errors
    assert "possible name/alias conflict" in messages(report)
    assert exact_key(first) != exact_key(second)
    assert candidate_key(first) == candidate_key(second)


def test_simplified_traditional_are_not_converted():
    assert exact_key("发") != exact_key("發")
    assert candidate_key("发") != candidate_key("發")


def test_sense_and_region_semantics(dataset, term, write):
    other = copy.deepcopy(term)
    other.update(id="st_d4d4c421-158f-402e-8364-14bbdb2b7fb9", sense="different-meaning")
    other["assessments"][0]["regions"] = ["TW"]
    other["assessments"][0]["context"] = "Different synthetic meaning in a different region."
    write(dataset, "sensitive/zh.jsonl", term, other)
    report = validate_dataset(dataset)
    assert not report.errors
    assert "possible name/alias conflict" in messages(report)


def test_multiple_categories_and_nonoverlapping_regions(dataset, term, write):
    term["assessments"][0]["regions"] = ["CN"]
    term["assessments"][0]["categories"] = ["context_dependent", "profanity"]
    term["assessments"].append(
        {"regions": ["TW"], "categories": ["context_dependent"], "risk": "low", "context": "测试"}
    )
    write(dataset, "sensitive/zh.jsonl", term)
    assert not validate_dataset(dataset).errors


@pytest.mark.parametrize("regions", [["CN"], ["001"]])
def test_overlapping_assessments_rejected(dataset, term, write, regions):
    term["assessments"][0]["regions"] = regions
    term["assessments"].append(
        {"regions": ["CN"], "categories": ["profanity"], "risk": "high", "context": "测试"}
    )
    write(dataset, "sensitive/zh.jsonl", term)
    assert "assessment regions overlap" in messages(validate_dataset(dataset))


def test_alias_conflict_and_within_record_duplicates(dataset, term, write):
    other = copy.deepcopy(term)
    other.update(id="st_d4d4c421-158f-402e-8364-14bbdb2b7fb9", term="另一个测试词")
    write(dataset, "sensitive/zh.jsonl", term, other)
    assert "possible name/alias conflict" in messages(validate_dataset(dataset))
    term["aliases"].append({"text": term["term"], "language": "zh", "kind": "alias"})
    write(dataset, "sensitive/zh.jsonl", term)
    assert "repeated name/alias" in messages(validate_dataset(dataset))


def test_entities_and_terms_are_never_compared(dataset, term, entity, write):
    entity["names"]["zh"] = term["term"]
    write(dataset, "sensitive/zh.jsonl", term)
    write(dataset, "entities/companies.jsonl", entity)
    assert not validate_dataset(dataset).issues


def test_entity_homonyms_need_disambiguation(dataset, entity, write):
    other = copy.deepcopy(entity)
    other["id"] = "ne_a108ed56-c27e-4ec2-83f1-f6b10aab3cf0"
    write(dataset, "entities/companies.jsonl", entity, other)
    assert "duplicate entry" in messages(validate_dataset(dataset))
    other["disambiguation"] = "A different synthetic entity sharing the same name."
    write(dataset, "entities/companies.jsonl", entity, other)
    report = validate_dataset(dataset)
    assert not report.errors
    assert "possible name/alias conflict" in messages(report)


def test_global_entity_region_cannot_mix_with_local_regions(dataset, entity, write):
    entity["regions"] = ["001", "CN"]
    write(dataset, "entities/companies.jsonl", entity)
    assert validate_dataset(dataset).errors


@pytest.mark.parametrize("text", [" lead", "tail ", "a\u200bb", "a\nb", "a\ud800b", "a\u2028b"])
def test_unsafe_label_characters(dataset, term, text):
    term["term"] = text
    (dataset / "sensitive/zh.jsonl").write_text(json.dumps(term) + "\n", encoding="utf-8")
    assert validate_dataset(dataset).errors


def test_emoji_and_variation_selector_are_preserved(dataset, term, write):
    term["term"] = "测试✈️"
    write(dataset, "sensitive/zh.jsonl", term)
    report = validate_dataset(dataset)
    assert not report.errors
    assert report.entries[0].record["term"] == "测试✈️"


def test_infinite_exponent_in_extension(dataset, term, write):
    term["extensions"] = {"test:number": 1e300}
    path = write(dataset, "sensitive/zh.jsonl", term)
    path.write_text(path.read_text("utf-8").replace("1e+300", "1e999"), encoding="utf-8")
    assert "non-finite" in messages(validate_dataset(dataset))


def test_surrogate_in_nested_extension_key(dataset, term):
    term["extensions"] = {"test:nested": {"\ud800": "value"}}
    (dataset / "sensitive/zh.jsonl").write_text(json.dumps(term) + "\n", encoding="utf-8")
    assert "control/surrogate" in messages(validate_dataset(dataset))


@pytest.mark.parametrize("url", ["http://example.com", "https://", "https://user:pass@example.com"])
def test_source_url(dataset, term, write, url):
    term["sources"][0]["url"] = url
    write(dataset, "sensitive/zh.jsonl", term)
    assert validate_dataset(dataset).errors


def test_review_and_rights_gate(dataset, term, write):
    term["review"] = {"status": "pending"}
    term["sources"][0]["rights"]["basis"] = "unresolved"
    write(dataset, "sensitive/zh.jsonl", term)
    assert not validate_dataset(dataset, "pending").errors
    result = messages(validate_dataset(dataset))
    assert "unresolved reuse rights" in result
    assert "not allowed in stage" in result


def test_approved_review_requires_evidence(dataset, term, write):
    term["review"] = {"status": "approved"}
    write(dataset, "sensitive/zh.jsonl", term)
    assert validate_dataset(dataset).errors


def test_copied_material_needs_permission_evidence(dataset, term, write):
    term["sources"][0]["rights"]["basis"] = "permission"
    write(dataset, "sensitive/zh.jsonl", term)
    assert "evidence_url" in messages(validate_dataset(dataset))


def test_dates_and_file_routing(dataset, term, entity, write):
    term["created_at"] = "2026-10-21"
    write(dataset, "sensitive/en.jsonl", term)
    entity["entity_type"] = "person"
    write(dataset, "entities/companies.jsonl", entity)
    result = messages(validate_dataset(dataset))
    assert "created_at must not be after" in result
    assert "language does not match" in result
    assert "entity_type must be" in result


def test_wrong_review_and_source_dates(dataset, term, write):
    term["review"]["reviewed_at"] = "2026-10-22"
    term["sources"][0]["accessed_at"] = "2026-10-23"
    write(dataset, "sensitive/zh.jsonl", term)
    result = messages(validate_dataset(dataset))
    assert "reviewed_at must be between" in result
    assert "accessed_at must not be after" in result


def test_layout_missing_and_unexpected_files(dataset):
    (dataset / "sensitive/zh.jsonl").unlink()
    (dataset / "forgotten.jsonl").write_text("{}\n", encoding="utf-8")
    result = messages(validate_dataset(dataset))
    assert "cannot read file" in result
    assert "unexpected JSONL file" in result


def test_repository_and_examples():
    assert not validate_repository(include_examples=True).errors
    assert len(validate_dataset(REPO / "examples/data", "example").entries) == 3


def test_id_cannot_shadow_another_stage(tmp_path, term, write, monkeypatch):
    import scripts._lib as lib

    for stage in ["data", "pending"]:
        for relative in lib.LAYOUT:
            path = tmp_path / stage / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
    write(tmp_path / "data", "sensitive/zh.jsonl", term)
    term["review"] = {"status": "pending"}
    write(tmp_path / "pending", "sensitive/zh.jsonl", term)
    monkeypatch.setattr(lib, "REPO", tmp_path)
    assert "multiple stages" in messages(lib.validate_repository())
