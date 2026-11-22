# Test Results Documentation

**Task ID:** R26-T058  
**Target:** `math/Pascal-Triangle/Pascal-Triangle.py` -> `generate_pascal_triangle` (line 11)  
**Test Runner:** `work/R26-T058/check.py`  

---

## 1. Source Fixture Preconditions

Preconditions establishing data anchors in `math/Pascal-Triangle/Pascal-Triangle.py`:
- `if n <= 0: return []`: Source lines 12–13 (re-indexed lines 27–28)
- `triangle = []`: Source line 14 (re-indexed line 29)
- `row = [1]`: Source line 17 (re-indexed line 32)
- `generate_pascal_triangle(n)`: Source line 11

---

## 2. Test Execution Summary

Command:
```bash
python3 work/R26-T058/check.py
```

- **Tests Executed:** 5
- **Passed:** 5
- **Failures:** 0
- **Errors:** 0
- **Exit Code:** 0

---

## 3. Expected vs Actual Results Table

| Test Case | Description & Input | Expected Output Assertions | Actual Output & Result |
|---|---|---|---|
| `test_absent_result_failure_boundary_zero` | Absent-result failure boundary (`n = 0`) | Returns `[]`; caller state `caller_state` unmutated | Matched `[]`; caller state unmutated. **PASS** |
| `test_absent_result_failure_branch_negative` | Negative out-of-domain input (`n = -5`) | Returns `[]` sentinel | Matched `[]`. **PASS** |
| `test_smallest_valid_input_one_row` | Smallest valid non-empty input (`n = 1`) | Returns `[[1]]` | Matched `[[1]]`. **PASS** |
| `test_ordinary_valid_input_four_rows` | Ordinary valid input (`n = 4`) | Returns `[[1], [1, 1], [1, 2, 1], [1, 3, 3, 1]]` | All 4 rows matched exactly. **PASS** |
| `test_success_after_failure_sequence` | Sequence: `n = 0` immediately followed by `n = 3` | `[]` followed cleanly by `[[1], [1, 1], [1, 2, 1]]` without leakage | Sequence execution verified. **PASS** |

---

## 4. Failure Propagation Verification

When an assertion failure or test error is encountered, `check.py` halts execution, prints the failure trace, and explicitly terminates with non-zero exit code (`sys.exit(1)`).
