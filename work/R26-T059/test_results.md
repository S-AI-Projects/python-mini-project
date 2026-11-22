# Test Results Documentation

**Task ID:** R26-T059  
**Target:** `games/Spot-the-Difference/Spot-the-Difference.py` -> `print_puzzle` (line 46)  
**Test Runner:** `work/R26-T059/check.py`  

---

## 1. Source Fixture Preconditions

Preconditions establishing data anchors in `games/Spot-the-Difference/Spot-the-Difference.py`:
- `PUZZLES`: Source lines 15–43
- `print_puzzle(puzzle)`: Source line 46
- Row iteration: Source line 52 (re-indexed line 67)
- Ruler generator: Source line 55 (re-indexed line 70)

---

## 2. Test Execution Summary

Command:
```bash
python3 work/R26-T059/check.py
```

- **Tests Executed:** 3
- **Passed:** 3
- **Failures:** 0
- **Errors:** 0
- **Exit Code:** 0

---

## 3. Empirical Scaling Measurements

| Input Size Label | Dimensions ($R \times C$) | Total Characters | Median Time (s) | Range (s) | Time Complexity Model |
|---|---|---|---|---|---|
| **Small** | $3 \times 11$ | 33 | 0.000004 | 0.000004 | $\mathcal{O}(R \cdot C)$ |
| **Medium** | $10 \times 25$ | 250 | 0.000006 | 0.000001 | $\mathcal{O}(R \cdot C)$ |
| **Large** | $50 \times 100$ | 5000 | 0.000016 | 0.000001 | $\mathcal{O}(R \cdot C)$ |

---

## 4. Expected vs Actual Results Table

| Test Case | Description & Input | Expected Output Assertions | Actual Output & Result |
|---|---|---|---|
| `test_smallest_valid_input_single_character` | Smallest boundary ($1 \times 1$ puzzle) | Prompt header, `1. A      B`, ruler `   1` | All substrings matched; valid layout. **PASS** |
| `test_ordinary_valid_input_builtin_puzzle` | Ordinary puzzle ($3 \times 11$ built-in) | Formatted rows 1–3, correct whitespace, ruler `   12345678901` | Exact substring match; layout verified. **PASS** |
| `test_complexity_scaling_experiment` | Scaling experiment across 3 sizes, 5 reps | All sizes pass correctness checks; metrics collected | Clean monotonic scaling; 0 failures. **PASS** |

---

## 5. Failure Propagation Verification

When an assertion failure or test error is encountered, `check.py` halts execution, prints the failure trace, and explicitly terminates with non-zero exit code (`sys.exit(1)`).
