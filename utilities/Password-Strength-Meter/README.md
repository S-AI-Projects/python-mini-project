# 🛡️ Password Strength Meter

An educational checklist utility that evaluates password strings against a structured four-point complexity criteria checklist.

---

## 🎯 Purpose & Important Disclaimer

This project is designed as an **educational checklist tool**. It evaluates basic structural characteristics of a password.

> [!IMPORTANT]
> **DISCLAIMER**: This checklist evaluates basic structural rules and is **NOT** a calibrated security-strength estimate. It does not measure entropy, crack resistance, or vulnerability to breach dictionaries. It does not assign arbitrary or misleading ratings such as *"weak"*, *"medium"*, or *"strong"*.

---

## 📋 The 4 Checklist Criteria

Each rule is evaluated independently, producing a boolean result and a total satisfied count out of 4:

1. **Length**: The password must have a length of at least 12 characters (`len(password) >= 12`).
2. **Mixed Letter Case**: The password must contain at least one uppercase letter AND at least one lowercase letter (`c.isupper()` and `c.islower()`).
3. **Contains a Digit**: Evaluated using Python's `str.isdecimal()`. This strictly matches decimal digits `0` through `9`. Non-decimal numeric characters such as superscripts (e.g., `²` or `³`), which return `True` for `str.isdigit()`, are intentionally excluded by `str.isdecimal()` and do not satisfy this check unless a standard decimal digit is present.
4. **Contains a Symbol**: Evaluated strictly as any character in Python's standard `string.punctuation` (`!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~`).

### Character Classification Rules
- **Non-ASCII Letters**: Evaluated using Python's Unicode-aware `.isupper()` and `.islower()`. Accented characters and international letters with case distinctions contribute toward the mixed case requirement.
- **Whitespace**: Whitespace characters (spaces, tabs, newlines) are **NOT** symbols. Whitespace characters contribute only to length.

---

## 📐 Invariants

The implementation guarantees five mathematical invariants across all inputs:

- **Invariant A (Bounded True Count)**: For every string input, `count_satisfied(results) == sum(1 for v in results.values() if v)` and `0 <= count <= 4`.
- **Invariant B (Empty String Zero State)**: An empty string `""` yields `False` for every condition and a count of `0`.
- **Invariant C (Monotonicity under Character Append)**: Appending any character `c` to a string `s` never causes a satisfied condition to become unsatisfied. Therefore, `count_satisfied(check_password(s + c)) >= count_satisfied(check_password(s))`.
- **Invariant D (Order Independence / Permutation Invariance)**: Shuffling or rearranging the characters in a password string produces identical condition results and score.
- **Invariant E (Length Boundary)**: Lengths 0, 1, and 11 fail the length check; lengths 12 and 13 pass.

---

## 🔍 Examples

### Example 1: Full Criteria Met
- **Input**: `"Abcdefghij1!"` (Length: 12)
- **Checklist**:
  - `Length >= 12`: ✅ PASS
  - `Mixed Case`: ✅ PASS (`'A'` uppercase, `'bcdefghij'` lowercase)
  - `Decimal Digit`: ✅ PASS (`'1'`)
  - `Punctuation Symbol`: ✅ PASS (`'!'`)
- **Criteria Satisfied**: `4/4`

### Example 2: Partial Criteria Met
- **Input**: `"Zq7@kmvx"` (Length: 8)
- **Checklist**:
  - `Length >= 12`: ❌ FAIL (8 < 12)
  - `Mixed Case`: ✅ PASS (`'Z'` uppercase, `'qkmvx'` lowercase)
  - `Decimal Digit`: ✅ PASS (`'7'`)
  - `Punctuation Symbol`: ✅ PASS (`'@'`)
- **Criteria Satisfied**: `3/4`

---

## 💻 CLI Usage

### Interactive Mode (Recommended)
Run without arguments to enter password securely via `getpass` (input is masked and not echoed):

```bash
python3 utilities/Password-Strength-Meter/main.py
```

### Argument Mode (For Testing / Automation)
You can optionally provide a single string argument:

```bash
python3 utilities/Password-Strength-Meter/main.py "Zq7@kmvx"
```

> [!WARNING]
> **Shell History Exposure**: Passing passwords via command-line arguments can expose them in shell history files (such as `~/.bash_history` or `~/.zsh_history`) and in system process tables (`ps`). Use interactive mode when testing sensitive credentials.

---

## 🧪 Running Tests

Run the test suite using Python's standard `unittest` discovery:

```bash
python3 -m unittest discover -s utilities/Password-Strength-Meter -p "test_*.py"
```
