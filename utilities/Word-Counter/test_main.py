"""Tests for utilities/Word-Counter/main.py (R26-T039).

Covers:
- Stated contract: "Tea, tea! coffee" -> {"tea": 2, "coffee": 1}; empty input -> {}
- Whitespace delimiting and case normalization
- Punctuation stripping policy (default and custom)
- Complexity experiment measuring bounded work at three domain sizes
- CLI behavior and side-effect-free import isolation
"""

import io
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    from . import main as word_mod
except ImportError:
    try:
        import main as word_mod
    except ImportError:
        import importlib.util
        _TARGET = Path(__file__).resolve().parent / "main.py"
        spec = importlib.util.spec_from_file_location("word_counter_test", _TARGET)
        word_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(word_mod)


class TestWordCounterContract(unittest.TestCase):
    """Verify exact core contract and required benchmarks."""

    def test_required_benchmark_example(self):
        """Verify: 'Tea, tea! coffee' gives {'tea': 2, 'coffee': 1}."""
        text = "Tea, tea! coffee"
        expected = {"tea": 2, "coffee": 1}
        actual = word_mod.count_words(text)
        self.assertEqual(actual, expected)

    def test_empty_input_returns_empty_dict(self):
        """Verify: empty input gives {}."""
        self.assertEqual(word_mod.count_words(""), {})

    def test_whitespace_only_returns_empty_dict(self):
        """Verify: whitespace-only string returns {}."""
        self.assertEqual(word_mod.count_words("   \t\n\r  "), {})

    def test_punctuation_only_returns_empty_dict(self):
        """Verify: tokens consisting solely of punctuation return {}."""
        self.assertEqual(word_mod.count_words(",,, ... !? --- ;:"), {})


class TestPunctuationAndNormalization(unittest.TestCase):
    """Verify case normalization and punctuation stripping rules."""

    def test_case_folding(self):
        """Different casing of the same word must normalize to lowercase."""
        text = "Hello HELLO hello HeLLo"
        self.assertEqual(word_mod.count_words(text), {"hello": 4})

    def test_leading_and_trailing_punctuation(self):
        """Punctuation on both sides of a word must be stripped."""
        text = '"(apple)" [banana], {cherry}!'
        expected = {"apple": 1, "banana": 1, "cherry": 1}
        self.assertEqual(word_mod.count_words(text), expected)

    def test_multiline_and_mixed_whitespace(self):
        """Tabs, newlines, and irregular spacing must delimit words correctly."""
        text = "one\ntwo\t\ttwo   three\n\nthree\tthree"
        expected = {"one": 1, "two": 2, "three": 3}
        self.assertEqual(word_mod.count_words(text), expected)

    def test_custom_punctuation_policy(self):
        """Supplying a custom punctuation set overrides the default policy."""
        # Strip only commas, leaving exclamation marks intact
        text = "Tea, tea! coffee,"
        result = word_mod.count_words(text, punctuation=",")
        self.assertEqual(result, {"tea": 1, "tea!": 1, "coffee": 1})

    def test_invalid_type_raises_type_error(self):
        """Non-string inputs must raise actionable TypeError."""
        for invalid_val in [123, None, ["tea"], {"text": "tea"}]:
            with self.subTest(val=invalid_val):
                with self.assertRaises(TypeError) as ctx:
                    word_mod.count_words(invalid_val)
                self.assertIn("Action:", str(ctx.exception))


class TestComplexityExperiment(unittest.TestCase):
    """Verify complexity measurements at three sizes with varying domain vocabularies."""

    def test_three_sizes_measured(self):
        """Experiment runs at 3 sizes (100, 1000, 10000) with domain variation."""
        sizes = (100, 1000, 10000)
        results = word_mod.run_complexity_experiment(sizes)
        self.assertEqual(len(results), 3)

        for i, size in enumerate(sizes):
            r = results[i]
            self.assertEqual(r["size_n"], float(size))
            self.assertGreater(r["bounded_operations"], 0)
            self.assertGreaterEqual(r["elapsed_seconds"], 0)
            self.assertIn("domain", r)

    def test_domain_vocabulary_varies_with_size(self):
        """Ensure vocabulary domain scales and varies across the three tiers."""
        results = word_mod.run_complexity_experiment((100, 1000, 10000))
        # Unique words found must reflect the domain variation (10, 100, 1000)
        self.assertEqual(results[0]["unique_words_found"], 10.0)
        self.assertEqual(results[1]["unique_words_found"], 100.0)
        self.assertEqual(results[2]["unique_words_found"], 1000.0)

    def test_linear_work_bound(self):
        """Verify bounded operations scale linearly O(N) relative to token count."""
        results = word_mod.run_complexity_experiment((100, 1000, 10000))
        ops_ratio_100_to_1000 = results[1]["bounded_operations"] / results[0]["bounded_operations"]
        # When N increases 10x (100 -> 1000), total operations should increase ~10x (linear)
        self.assertAlmostEqual(ops_ratio_100_to_1000, 10.0, delta=2.0)


class TestCliAndImportSafety(unittest.TestCase):
    """Verify CLI commands and confirm importing has no external side effects."""

    def test_cli_positional_arguments(self):
        stdout_buf = io.StringIO()
        with patch("sys.stdout", stdout_buf):
            exit_code = word_mod.main(["Tea,", "tea!", "coffee"])
        self.assertEqual(exit_code, 0)
        out = stdout_buf.getvalue()
        self.assertIn("tea: 2", out)
        self.assertIn("coffee: 1", out)

    def test_cli_experiment_flag(self):
        stdout_buf = io.StringIO()
        with patch("sys.stdout", stdout_buf):
            exit_code = word_mod.main(["--experiment"])
        self.assertEqual(exit_code, 0)
        out = stdout_buf.getvalue()
        self.assertIn("Size (N)", out)
        self.assertIn("100", out)
        self.assertIn("1000", out)
        self.assertIn("10000", out)

    def test_import_has_no_side_effects(self):
        """Importing the module must not prompt, print, or write files."""
        import importlib.util

        _target = Path(__file__).resolve().parent / "main.py"
        with patch("builtins.input") as mock_input, patch("sys.stdout") as mock_stdout:
            spec = importlib.util.spec_from_file_location("word_counter_isolated", _target)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            mock_input.assert_not_called()
            mock_stdout.write.assert_not_called()
            self.assertTrue(hasattr(mod, "count_words"))


if __name__ == "__main__":
    unittest.main()
