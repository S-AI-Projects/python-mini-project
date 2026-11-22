# Test Results Documentation

**Task ID:** R26-T055  
**Target:** `utilities/Tower-of-Hanoi/Tower-of-Hanoi.py` -> `main` (line 4)  
**Test Runner:** `work/R26-T055/check.py`  

---

## 1. Source Fixture Preconditions

Preconditions establishing data anchors in `utilities/Tower-of-Hanoi/Tower-of-Hanoi.py`:
- `towers = {"A": [], "B": [], "C": []}`: Source line 39 (re-indexed line 56)
- `tower_positions = {"A": 150, "B": 300, "C": 450}`: Source line 44 (re-indexed line 61)
- `main(root=None)`: Source line 4

---

## 2. Test Execution Summary

Command:
```bash
python3 work/R26-T055/check.py
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
| `test_smallest_valid_input_one_disk_contract` | Smallest valid input (`num_disks = 1`), injected `mock_root` | Towers state `{"A": [1], "B": [], "C": []}`; positions match; `mainloop` not blocked | Root returned; configured with geometry/title; no blocking. **PASS** |
| `test_ordinary_valid_input_three_disks_contract` | Ordinary input (`num_disks = 3`), injected `mock_root` | Towers state `{"A": [3, 2, 1], "B": [], "C": []}` | Configured correctly; clean return without side effects. **PASS** |
| `test_repeatability_and_state_isolation` | Successive invocations on two fresh mock roots | Distinct instances; identical deterministic configuration; zero state pollution | Isolated state preserved across runs; 0 leaks. **PASS** |
| `test_default_parameter_preserves_tk_instantiation` | Invocation with `root=None` (legacy callers) | Calls `tk.Tk()`, returns instance, runs `mainloop()` | Preserves full backward compatibility for existing callers. **PASS** |

---

## 4. Failure Propagation Verification

When an assertion failure or test error is encountered, `check.py` halts execution, prints the failure trace, and explicitly terminates with non-zero exit code (`sys.exit(1)`).
