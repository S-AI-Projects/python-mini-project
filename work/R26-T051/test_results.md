# Test Results Documentation

**Task ID:** R26-T051  
**Target:** `games/Word-Scramble-Game/Word-Scramble-Game.py` -> `clear` (line 82)  
**Test Runner:** `work/R26-T051/check.py`  

---

## 1. Source Fixture Preconditions

Preconditions establishing data anchors in `games/Word-Scramble-Game/Word-Scramble-Game.py`:
- `note = []`: Source line 276 (and re-indexed line 287)
- `valid_words = []`: Source line 345 (and re-indexed line 356)
- `clear()`: Source line 82

---

## 2. Test Execution Summary

Command:
```bash
python3 work/R26-T051/check.py
```

- **Tests Executed:** 3
- **Passed:** 3
- **Failures:** 0
- **Errors:** 0
- **Exit Code:** 0

---

## 3. Expected vs Actual Results Table

| Test Case | Description & Input | Expected Output Assertions | Actual Output & Result |
|---|---|---|---|
| `test_smallest_valid_input_nt_environment` | Inputs: `()`, `os.name='nt'`, `note=[]`, `valid_words=[]` | Return is `None`; `os.system("cls")` invoked once; `note` remains `[]`; `valid_words` remains `[]` | Return matched `None`; `cls` invoked; fixtures unmodified. **PASS** |
| `test_ordinary_input_posix_environment` | Inputs: `()`, `os.name='posix'`, `note=["hint used: −½ pts"]`, `valid_words=[("animals", ["tiger"])]` | Return is `None`; `os.system("clear")` invoked once; fixtures retain contents | Return matched `None`; `clear` invoked; fixtures unmodified. **PASS** |
| `test_domain_boundary_repeated_invocations` | Inputs: 5 repeated invocations under POSIX | Returns 5 `None`s; `os.system("clear")` called 5 times; fixtures unmodified | All 5 calls returned `None`; 5 calls dispatched; 0 mutations. **PASS** |

---

## 4. Failure Propagation Verification

When an assertion failure or test error is encountered, `check.py` halts execution, prints the failure trace, and explicitly terminates with non-zero exit code (`sys.exit(1)`).
