# Task R26-T031: Contract Lockdown for `play_sound` (`games/Math-Quiz/Math-Quiz.py`)

## 1. Baseline Analysis of `play_sound` (Line 21)

### Public Interface & Signature
```python
def play_sound(sound_type)
```

- **Public Inputs**:
  - `sound_type` (`str`): Identifies the audio cue to trigger.
  - Domain supported in game:
    * `'correct'` (line 575): Triggered on correct answer.
    * `'wrong'` (line 595): Triggered on incorrect answer.
    * `'game_over'` (line 605): Triggered when player lives reach 0.
  - Domain boundaries & edge cases:
    * Smallest valid input: `'wrong'` (length 5).
    * Ordinary input: `'correct'` (length 7).
    * Domain boundary input: `'game_over'` (length 9).
    * Unrecognized / empty input: `""`, `'unknown'`, etc.

- **Return Value**:
  - Always `None` (line 30 explicit return; line 40 end of block).

- **Mutation Behavior**:
  - Pure with respect to caller and global state: No mutation of module attributes, function attributes, or passed input arguments.

- **External Dependencies & I/O**:
  - `winsound` (Windows platform standard library):
    * `'correct'` -> `winsound.Beep(1000, 150)`
    * `'wrong'` -> `winsound.Beep(300, 300)`
    * `'game_over'` -> `winsound.Beep(200, 600)`
    * Unrecognized sound type -> no call to `winsound.Beep`
    * `RuntimeError` and `OSError` caught and suppressed.
  - `tkinter` / standard output fallback (non-Windows / headless platforms):
    * If `hasattr(tk, '_default_root') and tk._default_root`: calls `tk._default_root.bell()`.
    * Else: outputs ASCII bell `\a` to stdout (`print('\a', end='', flush=True)`).
    * `tk.TclError` and `OSError` caught and prints warning.

---

## 2. Fixtures & Source Data Anchors

The task anchors to question generation logic in `games/Math-Quiz/Math-Quiz.py`:

1. **Source Data Anchor 1 (Line 78)**:
   ```python
   a, b = random.randint(1, 60), random.randint(1, 60)
   ```
   - **Smallest valid input**: `a = 1, b = 1` (domain lower bound & repeated value).
     * Calculated sum: `1 + 1 = 2`.
     * Precondition: User answer `2` -> triggers `play_sound('correct')` (Line 575).
     * Precondition: User answer `!= 2` -> triggers `play_sound('wrong')` (Line 595).
   - **Ordinary input**: `a = 15, b = 25`.
     * Calculated sum: `15 + 25 = 40`.
     * Precondition: User answer `39` (incorrect) -> triggers `play_sound('wrong')` (Line 595).

2. **Source Data Anchor 2 (Line 127)**:
   ```python
   a, b = random.randint(1, 30), random.randint(1, 30)
   ```
   - **Domain boundary input**: `a = 30, b = 30` (domain upper bound & repeated value).
     * Calculated sum: `30 + 30 = 60`.
     * Precondition: Terminal incorrect answer depleting lives (`lives <= 0`) -> triggers `play_sound('game_over')` (Line 605).

---

## 3. Test Suites & Verification

- **Pytest Suite**: `tests/test_math_quiz.py`
  - 17 regression tests covering return value isolation, mutation isolation, winsound dispatch, fallback bells, exception suppression, and fixture data anchors.
- **Focused Runner**: `work/R26-T031/check.py`
  - Runs all checks, records tool versions and nonzero test count, produces `work/R26-T031/results.json` and `work/R26-T031/report.txt`, and exits with code 0 on full success.
