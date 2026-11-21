# Boundary Table & Domain Partition

**Task ID:** R26-T052  
**Target:** `games/Number-Guessing-Game/Number-Guessing-Game.py` -> `main`  

---

## 1. Domain Partition Table

| Input Domain | Partition Class | Values / Input | Source Contract Citation | Expected System Behavior |
|---|---|---|---|---|
| **Difficulty Selection** | Valid Boundary (Min attempts) | `"3"` | Line 24: `DIFFICULTY_ATTEMPTS["3"] = 5` | Allocates 5 attempts (Hard) |
| **Difficulty Selection** | Valid Interior | `"2"` | Line 23: `DIFFICULTY_ATTEMPTS["2"] = 10` | Allocates 10 attempts (Medium) |
| **Difficulty Selection** | Valid Boundary (Max attempts) | `"1"` | Line 22: `DIFFICULTY_ATTEMPTS["1"] = 15` | Allocates 15 attempts (Easy) |
| **Difficulty Selection** | Valid Default | `""` | Line 45: `default="2"` in `get_choice` | Resolves to Medium (10 attempts) |
| **Difficulty Selection** | Explicitly Unsupported | `"0"`, `"4"`, `"x"` | Line 44: `choices=["1", "2", "3"]` | Rejection: `"⚠️ Invalid selection. Please enter 1, 2 or 3."` |
| **Guess Range (`guess_num`)** | Unsupported (Below lower bound) | `0`, `-1` | Line 69: `if not (MIN_NUMBER <= guess_num <= MAX_NUMBER):` | Warning: `"⚠️ Enter a number between 1 and 100."`; attempt count unchanged; not in `guess_history` |
| **Guess Range (`guess_num`)** | Valid Boundary (Lower bound) | `1` (`MIN_NUMBER`) | Line 17: `MIN_NUMBER = 1` | Accepted; increments `attempts`; appended to `guess_history` |
| **Guess Range (`guess_num`)** | Valid Interior | `2` to `99` (e.g. `25`, `50`) | Line 69: `1 <= guess_num <= 100` | Accepted; proximity hints given; appended to `guess_history` |
| **Guess Range (`guess_num`)** | Valid Boundary (Upper bound) | `100` (`MAX_NUMBER`) | Line 18: `MAX_NUMBER = 100` | Accepted; increments `attempts`; appended to `guess_history` |
| **Guess Range (`guess_num`)** | Unsupported (Above upper bound) | `101`, `150` | Line 69: `if not (MIN_NUMBER <= guess_num <= MAX_NUMBER):` | Warning: `"⚠️ Enter a number between 1 and 100."`; attempt count unchanged; not in `guess_history` |
| **Guess Format (`guess_str`)** | Unsupported (Non-integer) | `"abc"`, `""` | Line 62: `get_int` | Warning: `"⚠️ Invalid input. Please enter a whole number."` / empty error |
| **Attempt Exhaustion** | Boundary (Loss trigger) | `attempts == max_attempts` | Line 59: `while attempts < max_attempts:` | Exits loop with `won=False`; prints `"💀 Out of attempts."` and all used attempts |
| **Play Again Selection** | Valid Exit Boundary | `'n'`, `'no'` | Line 115: `if again in ['n', 'no']:` | Prints `"👋 Goodbye."` and terminates `main()` |
| **Play Again Selection** | Valid Continue | `'y'`, `'yes'` | Line 111: `choices=['y', 'yes', 'n', 'no']` | Loops back to difficulty selection |
| **Play Again Selection** | Unsupported | `'maybe'`, `"1"` | Line 112: `error_invalid` | Rejection: `"⚠️ Invalid choice. Please enter 'y' or 'n'."` |

---

## 2. Boundary Verification Mapping

Each boundary has dedicated assertions placed on both sides:

1. **Lower Guess Boundary (0 vs 1):**
   - Below boundary (`0`): Emits error, does not increment `attempts`, does not pollute `guess_history`.
   - On boundary (`1`): Consumed as valid guess, increments `attempts`, recorded in `guess_history`.
2. **Upper Guess Boundary (100 vs 101):**
   - On boundary (`100`): Consumed as valid guess, increments `attempts`, recorded in `guess_history`.
   - Above boundary (`101`): Emits error, does not increment `attempts`, does not pollute `guess_history`.
3. **Attempt Budget Boundary (Smallest vs Default):**
   - Smallest valid (`"3"`): 5 attempts enforced (`DIFFICULTY_ATTEMPTS["3"]`).
   - Default (`""`): 10 attempts enforced (`DIFFICULTY_ATTEMPTS["2"]`).
