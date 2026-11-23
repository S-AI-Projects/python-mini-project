# Anagram Finder

A lightweight, reliable utility to find dictionary words that are anagrams of a given query word.

## Features
- **Accurate Letter Multiplicities:** Counts letter frequencies (e.g. repeated letters matter).
- **Case-Insensitive:** Compares words regardless of casing while preserving candidate casing in output.
- **Identity Exclusion:** Automatically excludes the query word itself.
- **Data Safety:** Never mutates caller lists and provides actionable error messages on invalid input types.

## Usage

### Programmatic
```python
from utilities.Anagram_Finder.main import find_anagrams

result = find_anagrams("listen", ["silent", "enlist", "listen", "banana"])
print(result)  # ['silent', 'enlist']
```

### Command Line
Run interactively:
```bash
python3 utilities/Anagram-Finder/main.py
```
Or with CLI arguments:
```bash
python3 utilities/Anagram-Finder/main.py listen silent enlist listen banana
```

## Running Tests
```bash
python3 -m unittest discover -s utilities/Anagram-Finder -p "test_*.py"
```
