# Palindrome Finder

A fast, lightweight utility to identify palindrome words (words that equal their reversal after lowercase normalization) while preserving source order and original casing.

## Features
- **Lowercase Normalization:** Correctly identifies palindromes regardless of letter casing (e.g., `Level` -> palindrome).
- **Source Casing & Order:** Preserves original capitalization and input order in output list.
- **Empty Word Policy:** Stated policy explicitly excludes empty strings (`""`) as non-palindromes.
- **Mutation-Resistant:** Unit test suite verifies rejection of deliberate mutations to the decisive matching condition.

## Usage

### Programmatic
```python
from utilities.Palindrome_Finder.main import find_palindromes

result = find_palindromes(["Level", "cat", "radar"])
print(result)  # ['Level', 'radar']
```

### Command Line
Run interactively:
```bash
python3 utilities/Palindrome-Finder/main.py
```
Or with CLI arguments:
```bash
python3 utilities/Palindrome-Finder/main.py Level cat radar
```

## Running Tests
```bash
python3 -m unittest discover -s utilities/Palindrome-Finder -p "test_*.py"
```
