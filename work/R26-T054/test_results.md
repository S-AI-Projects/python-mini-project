# Test Results Documentation

**Task ID:** R26-T054  
**Target:** `utilities/Text-to-Morse/Text-to-Morse.py` -> `_sleep_ms` (line 37)  
**Test Runner:** `work/R26-T054/check.py`  

---

## 1. Source Fixture Preconditions

Preconditions establishing data anchors in `utilities/Text-to-Morse/Text-to-Morse.py`:
- `DOT_DURATION = 100`: Source line 29
- `DASH_DURATION = 300`: Source line 30
- `morse_result = []`: Source line 109 (and re-indexed line 120)
- `unsupported_chars = []`: Source line 110 (and re-indexed line 121)
- `_sleep_ms(ms)`: Source line 37

---

## 2. Test Execution Summary

Command:
```bash
python3 work/R26-T054/check.py
```

- **Tests Executed:** 3 (including 100 bounded property samples)
- **Passed:** 3
- **Failures:** 0
- **Errors:** 0
- **Exit Code:** 0

---

## 3. Expected vs Actual Results Table

| Test Case | Description & Input | Expected Output Assertions | Actual Output & Result |
|---|---|---|---|
| `test_smallest_valid_input_zero_ms` | Input: `ms = 0`, `morse_result = []`, `unsupported_chars = []` | Return is `None`; `time.sleep(0.0)` called once; fixtures unmodified | Return matched `None`; `time.sleep(0.0)` verified; fixtures untouched. **PASS** |
| `test_ordinary_valid_input_dot_duration` | Input: `ms = 100`, populated fixtures | Return is `None`; `time.sleep(0.1)` called once; fixtures unmodified | Return matched `None`; `time.sleep(0.1)` verified; fixtures untouched. **PASS** |
| `test_invariant_random_property_generator` | 100 pseudo-random inputs `ms` in `[0, 5000]`, fixed seed=42 | Return is `None` for all; duration equals `ms / 1000.0`; monotonic ordering preserved | All 100 cases satisfied linearity, monotonicity, and purity invariants. **PASS** |

---

## 4. Failure Propagation Verification

When an assertion failure or test error is encountered, `check.py` halts execution, prints the failure trace, and explicitly terminates with non-zero exit code (`sys.exit(1)`).
