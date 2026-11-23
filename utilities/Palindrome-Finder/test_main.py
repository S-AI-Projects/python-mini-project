"""
Mutation-resistant unit tests for utilities/Palindrome-Finder/main.py (Task R26-T050).
"""

import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parent / "main.py"
spec = importlib.util.spec_from_file_location("palindrome_finder", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
is_palindrome = mod.is_palindrome
find_anagrams = mod.find_palindromes


class TestPalindromeFinder(unittest.TestCase):
    def test_stated_requirement_level_cat_radar(self):
        # [Level,cat,radar] -> [Level,radar]
        words = ["Level", "cat", "radar"]
        expected = ["Level", "radar"]
        actual = mod.find_palindromes(words)
        self.assertEqual(actual, expected)

    def test_empty_word_policy(self):
        # Empty string handled by stated policy: excluded as non-palindrome
        self.assertFalse(is_palindrome(""))
        words = ["", "radar", "", "world"]
        self.assertEqual(mod.find_palindromes(words), ["radar"])

    def test_preserves_source_casing_and_order(self):
        words = ["Kayak", "Noon", "rotor", "Racecar", "Civic"]
        expected = ["Kayak", "Noon", "rotor", "Racecar", "Civic"]
        self.assertEqual(mod.find_palindromes(words), expected)

    def test_caller_list_not_mutated(self):
        words = ["Level", "cat", "radar"]
        backup = list(words)
        _ = mod.find_palindromes(words)
        self.assertEqual(words, backup)

    def test_invalid_type_error(self):
        with self.assertRaises(TypeError):
            mod.find_palindromes("not-a-list")
        with self.assertRaises(TypeError):
            mod.find_palindromes(["valid", 123])

    def test_mutation_case_sensitive_mutant_rejected(self):
        # Deliberate mutant: case-sensitive check (word == word[::-1])
        # For "Level", mutant returns False, whereas contract requires True
        def mutant_case_sensitive(word):
            return len(word) > 0 and word == word[::-1]

        self.assertFalse(mutant_case_sensitive("Level"))
        self.assertTrue(is_palindrome("Level"))

    def test_mutation_empty_word_mutant_rejected(self):
        # Deliberate mutant: missing len > 0 check
        def mutant_empty_word(word):
            normalized = word.lower()
            return normalized == normalized[::-1]

        # Mutant accepts empty string "", our contract rejects it
        self.assertTrue(mutant_empty_word(""))
        self.assertFalse(is_palindrome(""))

    def test_mutation_inverted_condition_rejected(self):
        # Deliberate mutant: inverted condition
        def mutant_inverted(word):
            normalized = word.lower()
            return len(normalized) > 0 and normalized != normalized[::-1]

        self.assertFalse(mutant_inverted("radar"))
        self.assertTrue(is_palindrome("radar"))


if __name__ == "__main__":
    unittest.main()
