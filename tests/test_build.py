import copy
import hashlib
import json

import pytest

from scripts._lib import build_dataset, canonical_jsonl


def snapshot(root):
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


def test_export_separates_entities_and_keeps_variants(dataset, tmp_path, term, entity, write):
    term["aliases"] += [
        {"text": "ABC", "language": "en", "kind": "alias"},
        {"text": "ＡＢＣ", "language": "en", "kind": "variant"},
        {"text": "abc", "language": "en", "kind": "variant"},
    ]
    write(dataset, "sensitive/zh.jsonl", term)
    write(dataset, "entities/companies.jsonl", entity)
    output = tmp_path / "dist"
    assert not build_dataset(dataset, output).errors
    assert (output / "sensitive/en.txt").read_text("utf-8") == "ABC\nabc\nＡＢＣ\n"
    assert (output / "sensitive/zh.txt").read_text("utf-8").splitlines() == sorted(
        [term["term"], "示例佔位詞"]
    )
    assert entity["names"]["zh"] not in (output / "sensitive/zh.txt").read_text("utf-8")
    assert json.loads((output / "entities/companies.json").read_text("utf-8")) == [entity]
    assert json.loads((output / "sensitive/terms.json").read_text("utf-8")) == [term]
    manifest = json.loads((output / "manifest.json").read_text("utf-8"))
    assert manifest["record_counts"] == {"sensitive": 1, "entities": 1}
    for name, digest in manifest["files"].items():
        assert hashlib.sha256((output / name).read_bytes()).hexdigest() == digest


def test_reproducible_when_input_order_changes(dataset, tmp_path, term, write):
    other = copy.deepcopy(term)
    other.update(id="st_d4d4c421-158f-402e-8364-14bbdb2b7fb9", term="另一测试词")
    write(dataset, "sensitive/zh.jsonl", term, other)
    one, two = tmp_path / "one", tmp_path / "two"
    assert not build_dataset(dataset, one).errors
    write(dataset, "sensitive/zh.jsonl", other, term)
    assert not build_dataset(dataset, two).errors
    assert snapshot(one) == snapshot(two)
    # Identical aliases across records are exported only once.
    assert (one / "sensitive/zh.txt").read_text("utf-8").splitlines().count("示例佔位詞") == 1


def test_deprecated_is_excluded_and_stale_exports_are_replaced(dataset, tmp_path, term, write):
    write(dataset, "sensitive/zh.jsonl", term)
    output = tmp_path / "dist"
    build_dataset(dataset, output)
    (output / "unrelated.txt").write_text("keep", encoding="utf-8")
    term["review"]["status"] = "deprecated"
    write(dataset, "sensitive/zh.jsonl", term)
    assert not build_dataset(dataset, output).errors
    assert (output / "sensitive/zh.txt").read_bytes() == b""
    assert json.loads((output / "sensitive/terms.json").read_text()) == []
    assert (output / "unrelated.txt").read_text() == "keep"


def test_invalid_or_pending_data_never_updates_output(dataset, tmp_path, term, write):
    output = tmp_path / "dist"
    write(dataset, "sensitive/zh.jsonl", term)
    build_dataset(dataset, output)
    before = snapshot(output)
    term["review"] = {"status": "pending"}
    write(dataset, "sensitive/zh.jsonl", term)
    assert build_dataset(dataset, output).errors
    assert snapshot(output) == before


def test_source_and_output_cannot_overlap(dataset):
    with pytest.raises(ValueError, match="must not contain"):
        build_dataset(dataset, dataset)
    with pytest.raises(ValueError, match="must not contain"):
        build_dataset(dataset, dataset / "output")


def test_format_preserves_ids_and_original_unicode(term):
    term["term"] = "cafe\u0301"
    original = copy.deepcopy(term)
    formatted = canonical_jsonl([term])
    assert formatted.endswith("\n")
    assert json.loads(formatted) == original
    assert term == original
    assert "cafe\u0301" in formatted
