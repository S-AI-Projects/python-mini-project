# Test Results Documentation

**Task ID:** R26-T056  
**Target:** `games/Blackjack-21/suits.py` -> `get_heart_points` (line 7)  
**Test Runner:** `work/R26-T056/check.py`  

---

## 1. Source Fixture Preconditions

Preconditions establishing data anchors in `games/Blackjack-21/suits.py`:
- `SUIT_CACHE = {}`: Source line 5
- `points = []`: Source line 9 (re-indexed line 18)
- `get_heart_points(cx, cy, scale, invert=False)`: Source line 7

---

## 2. Test Execution Summary

Command:
```bash
python3 work/R26-T056/check.py
```

- **Tests Executed:** 4
- **Passed:** 4
- **Failures:** 0
- **Errors:** 0
- **Exit Code:** 0

---

## 3. Expected vs Actual Results Table

| Test Case | Description & Input | Expected Output Assertions | Actual Output & Result |
|---|---|---|---|
| `test_smallest_valid_input_zero_scale` | Smallest boundary (`cx=0, cy=0, scale=0, invert=False`) | Exactly 360 points all equal to `(0.0, 0.0)`; `SUIT_CACHE` untouched | Length=360, all `(0.0, 0.0)`; 0 mutations. **PASS** |
| `test_ordinary_valid_input_upright_heart` | Upright heart (`cx=100, cy=100, scale=1.5, invert=False`) | 360 parametric points matching independent reference math to 9 decimal places | Exact float parity across all 360 coordinate pairs. **PASS** |
| `test_ordinary_valid_input_inverted_spade` | Inverted spade (`cx=80, cy=120, scale=2.0, invert=True`) | 360 parametric points with inverted Y matching canonical reference | Exact float parity across all 360 coordinate pairs. **PASS** |
| `test_cache_isolation_and_purity` | Repeated calls with varied inputs | `SUIT_CACHE` length and keys remain unchanged | Cache purity preserved; 0 leakage. **PASS** |

---

## 4. Failure Propagation Verification

When an assertion failure or test error is encountered, `check.py` halts execution, prints the failure trace, and explicitly terminates with non-zero exit code (`sys.exit(1)`).
