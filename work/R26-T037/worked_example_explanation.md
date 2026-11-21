# R26-T037: FLAMES Game — Executable Worked Example for `main()`

## Overview
This document explains the execution of `main()` in `games/FLAMES-Game/FLAMES-Game.py` from initial user input through intermediate data state transitions to the final output.

## Source Data Anchors & Preconditions
- **Anchor 1 (Line 5):**
  `session = {"rounds": 0, "results": {r: 0 for r in "FLAMES"}, "total_score": 0}`
- **Anchor 2 (Line 80):**
  `flames = ['F', 'L', 'A', 'M', 'E', 'S']`
- **Input Preconditions (Lines 34-45):**
  Both names must be non-empty alphabetic strings (`.isalpha() == True`). Stripped, lowercased, spaces removed.
- **Letter Cancellation (Lines 52-55):**
  Common letters are removed one-by-one using list copy iteration (`for char in name1_list[:]`).
- **Remaining Count (Line 57):**
  `count = len(name1_list) + len(name2_list)`.
- **Degenerate Check (Line 62):**
  If `count == 0`, game calculation is skipped with `valid_game = False`.
- **Score Formula (Line 75):**
  `score = 30 + round((matched_chars / total_len) * 70)` if `total_len > 0` else `0`.

---

## 1. Smallest Valid Input Example
- **Inputs:** `name1 = "a"`, `name2 = "b"`, `choice = "n"`
- **Intermediate States:**
  1. `original_name1 = "a"`, `original_name2 = "b"`
  2. `name1_list = ['a']`, `name2_list = ['b']`
  3. No common letters found -> `count = 1 + 1 = 2`
  4. `valid_game = True`
  5. `total_len = 2`, `matched_chars = 0`
  6. `score = 30 + round((0 / 2) * 70) = 30%`

### Decisive State Transition (Cyclic Elimination)
Starting list: `flames = ['F', 'L', 'A', 'M', 'E', 'S']` (len = 6), `count = 2`, `index = 0`.
The elimination formula is: `index = (index + count - 1) % len(flames)`.

| Round | Current `flames` | Length | Formula `(index + 2 - 1) % len` | Eliminated Letter | Remaining `flames` | Next `index` |
|:-----:|:-----------------|:------:|:--------------------------------:|:-----------------:|:-------------------|:------------:|
| 1 | `['F', 'L', 'A', 'M', 'E', 'S']` | 6 | `(0 + 1) % 6 = 1` | `'L'` | `['F', 'A', 'M', 'E', 'S']` | 1 |
| 2 | `['F', 'A', 'M', 'E', 'S']` | 5 | `(1 + 1) % 5 = 2` | `'M'` | `['F', 'A', 'E', 'S']` | 2 |
| 3 | `['F', 'A', 'E', 'S']` | 4 | `(2 + 1) % 4 = 3` | `'S'` | `['F', 'A', 'E']` | 3 |
| 4 | `['F', 'A', 'E']` | 3 | `(3 + 1) % 3 = 1` | `'A'` | `['F', 'E']` | 1 |
| 5 | `['F', 'E']` | 2 | `(1 + 1) % 2 = 0` | `'F'` | `['E']` | 0 |

- **Decisive Final State:** Exactly one element remains: `flames = ['E']`.
- **Result:** `result = 'E'` -> `mapping['E'] = {"rel": "Enemies", "emoji": "😈", "metric": "Rivalry Quotient"}`.
- **Session Stats:** `session["rounds"] = 1`, `session["results"]["E"] = 1`, `session["total_score"] = 30`.

---

## 2. Ordinary Input Example
- **Inputs:** `name1 = "alex"`, `name2 = "emma"`, `choice = "n"`
- **Intermediate States:**
  1. `name1_list = ['a', 'l', 'e', 'x']`, `name2_list = ['e', 'm', 'm', 'a']`
  2. Cancellation:
     - `'a'` in `name2_list` -> removed from both
     - `'e'` in `name2_list` -> removed from both
     - Result: `name1_list = ['l', 'x']`, `name2_list = ['m', 'm']`
  3. `count = 2 + 2 = 4`
  4. `total_len = 8`, `matched_chars = 4`
  5. `score = 30 + round((4 / 8) * 70) = 30 + 35 = 65%`

### Decisive State Transition (Cyclic Elimination)
Starting list: `flames = ['F', 'L', 'A', 'M', 'E', 'S']`, `count = 4`, `index = 0`.

| Round | Current `flames` | Length | Formula `(index + 4 - 1) % len` | Eliminated Letter | Remaining `flames` | Next `index` |
|:-----:|:-----------------|:------:|:--------------------------------:|:-----------------:|:-------------------|:------------:|
| 1 | `['F', 'L', 'A', 'M', 'E', 'S']` | 6 | `(0 + 3) % 6 = 3` | `'M'` | `['F', 'L', 'A', 'E', 'S']` | 3 |
| 2 | `['F', 'L', 'A', 'E', 'S']` | 5 | `(3 + 3) % 5 = 1` | `'L'` | `['F', 'A', 'E', 'S']` | 1 |
| 3 | `['F', 'A', 'E', 'S']` | 4 | `(1 + 3) % 4 = 0` | `'F'` | `['A', 'E', 'S']` | 0 |
| 4 | `['A', 'E', 'S']` | 3 | `(0 + 3) % 3 = 0` | `'A'` | `['E', 'S']` | 0 |
| 5 | `['E', 'S']` | 2 | `(0 + 3) % 2 = 1` | `'S'` | `['E']` | 1 |

- **Decisive Final State:** `flames = ['E']`.
- **Result:** `result = 'E'` -> Enemies 😈, Rivalry Quotient: 65%.
