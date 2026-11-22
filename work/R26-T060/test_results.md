# Test Results Documentation

**Task ID:** R26-T060  
**Target:** `games/Emoji-Memory-Game/Emoji-Memory-Game.py` -> `is_browser` (line 26)  
**Test Runner:** `work/R26-T060/check.py`  

---

## 1. Source Fixture Preconditions

Preconditions establishing data anchors in `games/Emoji-Memory-Game/Emoji-Memory-Game.py`:
- `EMOJIS = ["🍎", "🚗", "⚽", "🐍", "🎧", "🔥", "🌈", "🚀"]`: Source line 9
- `DIFFICULTY_TIME_LIMITS = {"1": 5, "2": 4, "3": 2}`: Source lines 12–16
- `is_browser()`: Source line 26

---

## 2. Test Execution Summary

Command:
```bash
python3 work/R26-T060/check.py
```

- **Tests Executed:** 3
- **Passed:** 3
- **Failures:** 0
- **Errors:** 0
- **Exit Code:** 0

---

## 3. Mutation Resistance Verification

| Implementation | Tested Function | `sys.platform` | Expected Return | Actual Result | Status |
|---|---|---|---|---|---|
| **Original Implementation** | `sys.platform == 'emscripten'` | `'emscripten'` | `True` | `True` | **PASS** |
| **Plausible Mutant** | `sys.platform != 'emscripten'` | `'emscripten'` | `True` | `False` | **FAILED (Detected by `test_browser_platform_detection_emscripten`)** |

---

## 4. Expected vs Actual Results Table

| Test Case | Description & Input | Expected Output Assertions | Actual Output & Result |
|---|---|---|---|
| `test_browser_platform_detection_emscripten` | Smallest valid boundary (`sys.platform = "emscripten"`) | Returns `True`; `EMOJIS` & `DIFFICULTY_TIME_LIMITS` unmutated | Return `True`; 0 fixture mutations. **PASS** |
| `test_ordinary_desktop_platforms_return_false` | Ordinary OS platforms (`"darwin"`, `"linux"`, `"win32"`) | Returns `False` for each host platform | All returned `False`. **PASS** |
| `test_subtle_prefix_or_substring_rejection` | Non-exact platform strings (`"wasi"`, `"emscripten_v2"`) | Returns `False` (protects against loose `in` checks) | All returned `False`. **PASS** |

---

## 5. Failure Propagation Verification

When an assertion failure or test error is encountered, `check.py` halts execution, prints the failure trace, and explicitly terminates with non-zero exit code (`sys.exit(1)`).
