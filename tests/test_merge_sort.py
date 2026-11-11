import unittest
from unittest.mock import patch
import io
import os
import importlib.util

# Absolute path to Merge-Sort.py
file_path = os.path.join(
    os.path.dirname(__file__), "..",
    "math", "Merge-Sort", "Merge-Sort.py"
)
file_path = os.path.abspath(file_path)

# Load module dynamically
spec = importlib.util.spec_from_file_location("merge_sort_module", file_path)
merge_sort_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(merge_sort_module)

merge_sort = merge_sort_module.merge_sort
merge = merge_sort_module.merge
main = merge_sort_module.main


class TestMergeSort(unittest.TestCase):

    def test_merge_sort_ascending(self):
        self.assertEqual(merge_sort([64, 34, 25, 12, 22, 11, 90]), [11, 12, 22, 25, 34, 64, 90])
        self.assertEqual(merge_sort([5, 1, 4, 2, 8]), [1, 2, 4, 5, 8])

    def test_merge_sort_descending(self):
        self.assertEqual(merge_sort([64, 34, 25, 12, 22, 11, 90], reverse=True), [90, 64, 34, 25, 22, 12, 11])
        self.assertEqual(merge_sort([5, 1, 4, 2, 8], reverse=True), [8, 5, 4, 2, 1])

    def test_merge_sort_empty_and_single_item(self):
        self.assertEqual(merge_sort([]), [])
        self.assertEqual(merge_sort([42]), [42])

    def test_merge_sort_negative_integers(self):
        self.assertEqual(merge_sort([-5, -1, -10, 0, 5]), [-10, -5, -1, 0, 5])
        self.assertEqual(merge_sort([-5, -1, -10, 0, 5], reverse=True), [5, 0, -1, -5, -10])

    def test_merge_sort_already_sorted(self):
        self.assertEqual(merge_sort([1, 2, 3, 4, 5]), [1, 2, 3, 4, 5])
        self.assertEqual(merge_sort([5, 4, 3, 2, 1], reverse=True), [5, 4, 3, 2, 1])

    def test_merge_sort_with_duplicates(self):
        self.assertEqual(merge_sort([5, 3, 8, 3, 9, 1, 5]), [1, 3, 3, 5, 5, 8, 9])

    def test_merge_sort_does_not_mutate_original(self):
        original = [5, 3, 1, 4, 2]
        original_copy = original.copy()
        merge_sort(original)
        self.assertEqual(original, original_copy)

    def test_merge_ascending(self):
        self.assertEqual(merge([1, 3, 5], [2, 4, 6]), [1, 2, 3, 4, 5, 6])

    def test_merge_descending(self):
        self.assertEqual(merge([5, 3, 1], [6, 4, 2], reverse=True), [6, 5, 4, 3, 2, 1])

    def test_merge_empty_left(self):
        self.assertEqual(merge([], [1, 2, 3]), [1, 2, 3])

    def test_merge_empty_right(self):
        self.assertEqual(merge([1, 2, 3], []), [1, 2, 3])

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_main_flow_ascending(self, mock_stdout, mock_input):
        mock_input.side_effect = ["64 34 25", "1", "n"]
        main()
        output = mock_stdout.getvalue()
        self.assertIn("Original list: [64, 34, 25]", output)
        self.assertIn("Sorted list (Ascending): [25, 34, 64]", output)

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_main_flow_descending(self, mock_stdout, mock_input):
        mock_input.side_effect = ["64 34 25", "2", "n"]
        main()
        output = mock_stdout.getvalue()
        self.assertIn("Original list: [64, 34, 25]", output)
        self.assertIn("Sorted list (Descending): [64, 34, 25]", output)

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_main_flow_invalid_inputs(self, mock_stdout, mock_input):
        mock_input.side_effect = ["", "64 abc 25", "64 34 25", "3", "64 34 25", "1", "y", "12 11", "2", "n"]
        main()
        output = mock_stdout.getvalue()
        self.assertIn("Error: Input cannot be empty!", output)
        self.assertIn("Error: Please enter valid integers only.", output)
        self.assertIn("Invalid sorting choice! Please select 1 or 2.", output)
        self.assertIn("Sorted list (Ascending): [25, 34, 64]", output)
        self.assertIn("Sorted list (Descending): [12, 11]", output)

    def test_documented_runnable_example_doctest(self):
        """Executes docstring examples using doctest with explicit namespace."""
        import doctest
        finder = doctest.DocTestFinder()
        tests = finder.find(merge_sort, globs={"merge_sort": merge_sort})
        self.assertTrue(len(tests) > 0, "No docstring tests found in merge_sort")
        runner = doctest.DocTestRunner(verbose=False)
        for t in tests:
            runner.run(t)
        self.assertEqual(runner.failures, 0, f"{runner.failures} docstring example(s) failed")
        self.assertGreater(runner.tries, 0, "No doctest examples were executed")

    def test_merge_sort_required_fixtures(self):
        """Verifies required fixtures including reverse=True, immutability, and smallest collection."""
        fixtures = [
            ([3, 1, 2], False, [1, 2, 3]),
            ([3, 1, 2], True, [3, 2, 1]),
            ([2, 2, 1], False, [1, 2, 2]),
            ([1, 2, 3], False, [1, 2, 3]),
            ([3, 2, 1], False, [1, 2, 3]),
            ([], False, []),
        ]
        for arr, rev, expected in fixtures:
            orig = arr.copy()
            result = merge_sort(arr, reverse=rev)
            self.assertEqual(result, expected)
            self.assertEqual(arr, orig, "Input list must not be mutated")


if __name__ == '__main__':
    unittest.main()