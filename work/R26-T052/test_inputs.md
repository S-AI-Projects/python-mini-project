# Test Inputs and Independently Calculated Expected Outputs

**Task ID:** R26-T052  
**Target File:** `games/Number-Guessing-Game/Number-Guessing-Game.py`  
**Target Function:** `main` (line 33)  

---

## 1. Source Fixture Preconditions & Line References

In `games/Number-Guessing-Game/Number-Guessing-Game.py`:

- **Fixture 1 (`DIFFICULTY_ATTEMPTS`):** Lines 21–25
  ```python
  21: DIFFICULTY_ATTEMPTS = {
  22:     "1": 15,
  23:     "2": 10,
  24:     "3": 5,
  25: }
  ```
  - Precondition: Sets the maximum allowed attempts based on chosen difficulty.
  - Selected at line 49: `max_attempts = DIFFICULTY_ATTEMPTS[choice]`.

- **Fixture 2 (`guess_history = []`):** Line 53
  ```python
  53:         guess_history = []
  ```
  - Precondition: Initialized to an empty list before each game round begins.
  - Appended at line 74: `guess_history.append(guess_num)`.

- **Constraint Constants:** Lines 17–18
  ```python
  17: MIN_NUMBER = 1
  18: MAX_NUMBER = 100
  ```
  - Boundary check at line 69: `if not (MIN_NUMBER <= guess_num <= MAX_NUMBER):`.

---

## 2. Literal Inputs & Independently Calculated Expected Outputs

All expected outputs were calculated independently prior to implementation editing.

### Case 1: Smallest Valid Input (Immediate Win on Smallest Budget)
- **Precondition Citations:**
  - `DIFFICULTY_ATTEMPTS["3"] = 5` (line 24)
  - `MIN_NUMBER = 1` (line 17)
  - `guess_history = []` (line 53)
- **Mocked Target Number:** `number = 1`
- **Literal Input Sequence:** `["3", "1", "n"]`
  - Difficulty: `"3"` (Hard, 5 attempts - smallest attempt domain)
  - Guess: `1` (smallest valid guess `MIN_NUMBER = 1`, immediate match)
  - Play Again: `'n'` (exit game)
- **Independently Calculated Outputs:**
  - `max_attempts`: `5`
  - `attempts`: `1`
  - `guess_history`: `[1]`
  - Output contains:
    - `"🎯 Attempts: 1/5"`
    - `"📜 Guesses: 1"`
    - `"🏆 You solved it in 1 guesses."`
    - `"👋 Goodbye."`

### Case 2: Ordinary Input (Multi-Guess Win Across Domain Interior)
- **Precondition Citations:**
  - `DIFFICULTY_ATTEMPTS["2"] = 10` (line 23)
  - `guess_history = []` (line 53)
- **Mocked Target Number:** `number = 50`
- **Literal Input Sequence:** `["2", "25", "75", "45", "50", "n"]`
  - Difficulty: `"2"` (Medium, 10 attempts)
  - Guess 1: `25` (interior valid, < 50, diff=25) -> `"📈 Too low."`, `"❄️ Far off."`
  - Guess 2: `75` (interior valid, > 50, diff=25) -> `"📉 Too high."`, `"❄️ Far off."`
  - Guess 3: `45` (interior valid, < 50, diff=5)  -> `"📈 Too low."`, `"😊 Close."`
  - Guess 4: `50` (interior valid, == 50)         -> `"🎉 Correct! You guessed the number."`
  - Play Again: `'n'`
- **Independently Calculated Outputs:**
  - `max_attempts`: `10`
  - `attempts`: `4`
  - `guess_history`: `[25, 75, 45, 50]`
  - Output contains:
    - `"🎯 Attempts: 4/10"`
    - `"📜 Guesses: 25, 75, 45, 50"`
    - `"🏆 You solved it in 4 guesses."`
    - `"👋 Goodbye."`

### Case 3: Lower Boundary Input Partition (Outside vs Inside)
- **Precondition Citations:**
  - `MIN_NUMBER = 1` (line 17)
  - Constraint check: `MIN_NUMBER <= guess_num <= MAX_NUMBER` (line 69)
- **Mocked Target Number:** `number = 1`
- **Literal Input Sequence:** `["3", "0", "1", "n"]`
  - Guess `0` (outside boundary, below `MIN_NUMBER`):
    - Rejected at line 69 without incrementing attempts.
    - Warning emitted: `"⚠️ Enter a number between 1 and 100."`
    - Next attempt still shows `5 left`.
  - Guess `1` (on boundary, smallest valid integer):
    - Accepted and matches target.
- **Independently Calculated Outputs:**
  - Attempts count: `1/5` (0 does not count)
  - `guess_history`: `[1]` (0 is not recorded)
  - Output contains:
    - `"⚠️ Enter a number between 1 and 100."`
    - `"🎯 Attempts: 1/5"`
    - `"📜 Guesses: 1"`

### Case 4: Upper Boundary Input Partition (Inside vs Outside)
- **Precondition Citations:**
  - `MAX_NUMBER = 100` (line 18)
  - Constraint check: `MIN_NUMBER <= guess_num <= MAX_NUMBER` (line 69)
- **Mocked Target Number:** `number = 100`
- **Literal Input Sequence:** `["3", "101", "100", "n"]`
  - Guess `101` (outside boundary, above `MAX_NUMBER`):
    - Rejected at line 69 without incrementing attempts.
    - Warning emitted: `"⚠️ Enter a number between 1 and 100."`
    - Next attempt still shows `5 left`.
  - Guess `100` (on boundary, maximum valid integer):
    - Accepted and matches target.
- **Independently Calculated Outputs:**
  - Attempts count: `1/5` (101 does not count)
  - `guess_history`: `[100]` (101 is not recorded)
  - Output contains:
    - `"⚠️ Enter a number between 1 and 100."`
    - `"🎯 Attempts: 1/5"`
    - `"📜 Guesses: 100"`

### Case 5: Loss Boundary (All Attempts Exhausted)
- **Precondition Citations:**
  - `DIFFICULTY_ATTEMPTS["3"] = 5` (line 24)
  - Loop condition: `while attempts < max_attempts:` (line 59)
  - Loss branch: `if not won:` (line 100)
- **Mocked Target Number:** `number = 50`
- **Literal Input Sequence:** `["3", "10", "20", "30", "40", "60", "n"]`
  - 5 unsuccessful guesses within range.
- **Independently Calculated Outputs:**
  - Attempts used: `5/5`
  - `guess_history`: `[10, 20, 30, 40, 60]`
  - Output contains:
    - `"💀 Out of attempts."`
    - `"The number was 50."`
    - `"📜 Your guesses: 10, 20, 30, 40, 60"`
    - `"❌ You used all 5 attempts."`

### Case 6: Difficulty Boundary Partition & Default Fallback
- **Precondition Citations:**
  - `get_choice` at line 42 with `choices=["1", "2", "3"]`, `default="2"`
- **Literal Input Sequence:** `["4", "", "50", "n"]` with target `number = 50`
  - `"4"` (invalid difficulty):
    - Rejected with `"⚠️ Invalid selection. Please enter 1, 2 or 3."`
  - `""` (empty string):
    - Resolves to default `"2"` (`DIFFICULTY_ATTEMPTS["2"] = 10`).
- **Independently Calculated Outputs:**
  - Warning emitted for `"4"`.
  - Game proceeds with `10 attempts`.
  - Correct guess `50` yields `"🎯 Attempts: 1/10"`.
