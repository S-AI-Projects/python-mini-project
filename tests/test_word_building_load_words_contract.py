"""Mutation-resistant output and isolation checks for _load_words."""

import importlib.util
import io
import json
from pathlib import Path
from unittest.mock import patch

import pytest


SOURCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "games"
    / "Word-Building"
    / "data.py"
)

# Smallest supported file input: one dictionary bucket with an empty word
# list. The expected parsed value is independently the same mapping.
SMALLEST_JSON = '{"a": []}'
SMALLEST_EXPECTED = {"a": []}

# Ordinary input deliberately includes an empty bucket and non-sorted word
# lists. JSON object/list order is preserved by the documented data contract.
ORDINARY_JSON = '{"a": ["zebra", "apple"], "b": ["Ball", "book"], "c": []}'
ORDINARY_EXPECTED = {
    "a": ["zebra", "apple"],
    "b": ["Ball", "book"],
    "c": [],
}


def _import_data(source_path, initial_import_data):
    spec = importlib.util.spec_from_file_location("word_building_test_data", source_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load word data module from {source_path}")
    module = importlib.util.module_from_spec(spec)
    with patch(
        "builtins.open",
        return_value=io.StringIO(json.dumps(initial_import_data)),
    ):
        spec.loader.exec_module(module)
    return module


def _load_from_fixture(tmp_path, source_path, literal_json, initial_import_data):
    module = _import_data(source_path, initial_import_data)
    words_path = tmp_path / "words.json"
    words_path.write_text(literal_json, encoding="utf-8")
    module.WORDS_FILE = words_path
    return module, words_path


def _assert_output_contract(module, expected, case):
    first = module._load_words()
    evidence = {
        "case": case,
        "source_precondition": (
            "data.py:11 defines _load_words; line 12 documents preservation "
            "of empty buckets/order; line 13 opens WORDS_FILE as UTF-8; "
            "line 14 returns json.load(fh)"
        ),
        "expected_type": "dict",
        "actual_type": type(first).__name__,
        "expected": expected,
        "actual": first,
        "expected_key_order": list(expected),
        "actual_key_order": list(first),
        "expected_list_order": {
            key: value for key, value in expected.items()
        },
        "actual_list_order": first,
    }
    print("R26_T020_CASE=" + json.dumps(evidence, ensure_ascii=False))

    assert isinstance(first, dict), f"{case} preserves buckets: expected dict"
    assert first == expected, (
        f"{case} preserves buckets and word order: "
        f"expected {expected!r}, got {first!r}"
    )
    assert list(first) == list(expected), (
        f"{case} preserves key order: expected {list(expected)!r}, "
        f"got {list(first)!r}"
    )
    return first


def test_smallest_valid_empty_bucket_is_preserved(tmp_path):
    module, words_path = _load_from_fixture(
        tmp_path, SOURCE_PATH, SMALLEST_JSON, {}
    )
    first = _assert_output_contract(
        module, SMALLEST_EXPECTED, "smallest valid empty bucket"
    )
    first["a"].append("temporary")

    second = module._load_words()
    assert second == SMALLEST_EXPECTED, (
        "fresh _load_words call must return fixture contents, "
        f"expected {SMALLEST_EXPECTED!r}, got {second!r}"
    )
    assert json.loads(words_path.read_text(encoding="utf-8")) == SMALLEST_EXPECTED


def test_ordinary_input_preserves_bucket_and_word_order(tmp_path):
    module, _ = _load_from_fixture(
        tmp_path, SOURCE_PATH, ORDINARY_JSON, {}
    )
    _assert_output_contract(
        module, ORDINARY_EXPECTED, "ordinary ordered word buckets"
    )
    second = module._load_words()
    assert second == ORDINARY_EXPECTED, (
        f"fresh read expected {ORDINARY_EXPECTED!r}, got {second!r}"
    )


def test_regression_detects_dropping_empty_buckets_in_mutant(tmp_path):
    original_source = SOURCE_PATH.read_text(encoding="utf-8")
    original_return = "return json.load(fh)"
    mutant_return = (
        "return {letter: words for letter, words in json.load(fh).items() if words}"
    )
    assert original_source.count(original_return) == 1
    mutant_path = tmp_path / "mutant_data.py"
    mutant_path.write_text(
        original_source.replace(original_return, mutant_return),
        encoding="utf-8",
    )
    mutant, _ = _load_from_fixture(
        tmp_path, mutant_path, SMALLEST_JSON, {}
    )
    actual = mutant._load_words()
    evidence = {
        "case": "one-line mutant drops empty buckets",
        "mutation": mutant_return,
        "input": json.loads(SMALLEST_JSON),
        "expected": SMALLEST_EXPECTED,
        "mutant_actual": actual,
        "killed_by_assertion": "smallest valid empty bucket preserves buckets",
        "semantic_reason": "the mutation drops a valid key whose bucket is empty",
    }
    print("R26_T020_MUTANT=" + json.dumps(evidence, ensure_ascii=False))

    with pytest.raises(AssertionError, match="smallest valid empty bucket preserves buckets"):
        _assert_output_contract(
            mutant, SMALLEST_EXPECTED, "smallest valid empty bucket"
        )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))
