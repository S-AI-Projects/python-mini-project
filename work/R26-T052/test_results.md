# Test Results Documentation

**Task ID:** R26-T052  
**Target:** `games/Number-Guessing-Game/Number-Guessing-Game.py` -> `main` (line 33)  
**Test Runner:** `work/R26-T052/check.py`  

---

## 1. Source Fixture Preconditions

Preconditions establishing data anchors in `games/Number-Guessing-Game/Number-Guessing-Game.py`:
- `DIFFICULTY_ATTEMPTS = {"1": 15, "2": 10, "3": 5}`: Source lines 21–25
- `guess_history = []`: Source line 53 (re-indexed line 79 after docstring)
- `MIN_NUMBER = 1, MAX_NUMBER = 100`: Source lines 17–18

---

## 2. Test Execution Summary

Command:
```bash
python3 work/R26-T052/check.py
```

- **Tests Executed:** 6
- **Passed:** 6
- **Failures:** 0
- **Errors:** 0
- **Exit Code:** 0

---

## 3. Expected vs Actual Results Table

| Test Case | Description & Input | Expected Output Assertions | Actual Output & Result |
|---|---|---|---|
| `test_smallest_valid_input_immediate_win` | Input: `["3", "1", "n"]`, Target: `1` | `You have 5 attempts.`, `🎯 Attempts: 1/5`, `📜 Guesses: 1`, `🏆 You solved it in 1 guesses.`, `👋 Goodbye.` | All substrings matched; attempts=1, guess_history=[1]. **PASS** |
| `test_ordinary_input_multi_guess_win` | Input: `["2", "25", "75", "45", "50", "n"]`, Target: `50` | `You have 10 attempts.`, `📈 Too low.`, `📉 Too high.`, `😊 Close.`, `🎯 Attempts: 4/10`, `📜 Guesses: 25, 75, 45, 50` | All substrings and hints matched; attempts=4, guess_history populated sequentially. **PASS** |
| `test_lower_boundary_inside_and_outside` | Input: `["3", "0", "1", "n"]`, Target: `1` | `⚠️ Enter a number between 1 and 100.`, `🎯 Attempts: 1/5`, `📜 Guesses: 1` | `0` rejected without penalty; `1` accepted; attempts=1. **PASS** |
| `test_upper_boundary_inside_and_outside` | Input: `["3", "101", "100", "n"]`, Target: `100` | `⚠️ Enter a number between 1 and 100.`, `🎯 Attempts: 1/5`, `📜 Guesses: 100` | `101` rejected without penalty; `100` accepted; attempts=1. **PASS** |
| `test_attempts_exhaustion_loss_boundary` | Input: `["3", "10", "20", "30", "40", "60", "n"]`, Target: `50` | `💀 Out of attempts.`, `The number was 50.`, `📜 Your guesses: 10, 20, 30, 40, 60`, `❌ You used all 5 attempts.` | All 5 attempts exhausted; loss screen rendered with complete history. **PASS** |
| `test_difficulty_boundary_and_default` | Input: `["4", "", "50", "n"]`, Target: `50` | `⚠️ Invalid selection. Please enter 1, 2 or 3.`, `You have 10 attempts.`, `🎯 Attempts: 1/10` | Unsupported `"4"` rejected; empty input fell back to default `"2"` (10 attempts). **PASS** |

---

## 4. Failure Propagation Verification

When an assertion failure or test error is encountered, `check.py` halts execution, prints the failure trace, and explicitly terminates with non-zero exit code (`sys.exit(1)`).
