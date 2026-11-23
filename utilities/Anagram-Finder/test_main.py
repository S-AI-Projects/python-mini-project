"""
Unit tests for utilities/Anagram-Finder/main.py (Task R26-T048).
"""

import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parent / "main.py"
spec = importlib.util.spec_from_file_location("anagram_finder", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
find_anagrams = mod.find_anagrams


class TestAnagramFinder(unittest.TestCase):
    def test_stated_requirement_listen_example(self):
        # listen with [silent,enlist,listen,banana] returns [silent,enlist]
        query = "listen"
        candidates = ["silent", "enlist", "listen", "banana"]
        expected = ["silent", "enlist"]
        actual = find_anagrams(query, candidates)
        self.assertEqual(actual, expected)

    def test_case_insensitivity_and_case_preservation(self):
        query = "Level"
        candidates = ["level", "leVel", "VELEL", "hello"]
        # Excludes exact case-insensitive matches ("level", "leVel")
        # Preserves source casing of matches ("VELEL")
        expected = ["VELEL"]
        actual = find_anagrams(query, candidates)
        self.assertEqual(actual, expected)

    def test_repeated_letter_counts_matter(self):
        query = "aabb"
        candidates = ["ab", "aab", "bbaa", "aaabbb"]
        expected = ["bbaa"]
        self.assertEqual(find_anagrams(query, candidates), expected)

    def test_caller_data_not_mutated(self):
        query = "listen"
        original = ["silent", "enlist", "listen", "banana"]
        backup = list(original)
        _ = find_anagrams(query, original)
        # Verify original list remains completely unchanged
        self.assertEqual(original, backup)

    def test_actionable_errors_on_invalid_query_type(self):
        with self.assertRaises(TypeError) as ctx:
            find_anagrams(12345, ["word"])
        self.assertIn("query must be a string", str(ctx.exception))

    def test_actionable_errors_on_invalid_candidates_type(self):
        with self.assertRaises(TypeError) as ctx:
            find_anagrams("test", 12345)
        self.assertIn("candidates must be a list or tuple", str(ctx.exception))

    def test_actionable_errors_on_invalid_candidate_element(self):
        with self.assertRaises(TypeError) as ctx:
            find_anagrams("test", ["valid", 999])
        self.assertIn("all candidate items must be strings", str(ctx.exception))

    def test_empty_candidates_returns_empty(self):
        self.assertEqual(find_anagrams("hello", []), [])


if __name__ == "__main__":
    unittest.main()
