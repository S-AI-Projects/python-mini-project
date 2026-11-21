# Roman Numeral Converter 🏛️

A robust, canonical Roman numeral encoder supporting integers from 1 to 3999 with failure-path isolation and actionable error messages.

## Features
- **Canonical Roman Numeral Encoding:** Full support for standard subtractive pairs (`IV`, `IX`, `XL`, `XC`, `CD`, `CM`).
- **Failure-Path Protection:** Pure non-mutating batch conversion (`convert_many`) and atomic file updates (`convert_file`) guarantee caller memory structures and filesystem targets remain 100% intact if any error occurs.
- **Actionable Error Messages:** Clear, informative error messages stating the received value/type, acceptable ranges, and exact corrective actions.
- **Import Safe:** Importing the module has zero side effects (no prompts, CLI executions, or disk writes).

---

## Supported Limits
- **Minimum Value:** `1` (represented as `I`)
- **Maximum Value:** `3999` (represented as `MMMCMXCIX`)
- **Rejected Values:**
  - `0`: Zero was not recognized in canonical Roman numerals (`ValueError`).
  - Negative integers (`< 0`): Rejected with actionable `ValueError`.
  - Numbers `>= 4000`: Standard numeral notation does not support values above 3999 without vinculum/apostrophus (`ValueError`).
  - Non-integer types (`float`, `str`, `bool`, `None`, etc.): Rejected with actionable `TypeError`.

---

## Exact Input / Output Examples

| Input Integer | Canonical Roman Output | Description |
|:---:|:---:|:---|
| `1` | `I` | Minimum supported integer |
| `4` | `IV` | Subtractive pair (5 - 1) |
| `9` | `IX` | Subtractive pair (10 - 1) |
| `58` | `LVIII` | 50 (L) + 5 (V) + 3 (III) |
| `1994` | `MCMXCIV` | 1000 (M) + 900 (CM) + 90 (XC) + 4 (IV) |
| `3999` | `MMMCMXCIX` | Maximum supported integer |

### Invalid Inputs & Actionable Error Messages

```python
>>> to_roman(0)
ValueError: Integer 0 is out of bounds [1..3999]. Zero has no representation in canonical Roman numerals. Action: Supply an integer within 1..3999.

>>> to_roman(3.14)
TypeError: Expected integer input in range 1..3999, got type float (3.14). Action: Convert or pass an integer value (e.g. to_roman(42)).
```

---

## Usage

### As a Python Module
```python
from utilities.Roman_Numerals.main import to_roman, convert_many, convert_file

# Single conversion
numeral = to_roman(1994)
print(numeral)  # 'MCMXCIV'

# Batch conversion (guaranteed non-mutating)
nums = [1, 4, 9, 58]
results = convert_many(nums)
print(results)  # ['I', 'IV', 'IX', 'LVIII']

# Atomic file conversion (target file untouched on failure)
convert_file("numbers.txt", "roman_output.txt")
```

### CLI Command
```bash
# Convert one or more numbers directly:
python3 utilities/Roman-Numerals/main.py 1 4 9 58 1994

# Convert a file with numbers:
python3 utilities/Roman-Numerals/main.py --file numbers.txt --output roman.txt

# Interactive prompt:
python3 utilities/Roman-Numerals/main.py
```

---

## Running Tests
Run the standard unit test discovery:
```bash
python3 -m unittest discover -s utilities/Roman-Numerals -p "test_*.py"
```
Or via pytest:
```bash
pytest utilities/Roman-Numerals/test_main.py -v
```
