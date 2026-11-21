# Test Inputs and Independently Calculated Expected Outputs

**Task ID:** R26-T051  
**Target File:** `games/Word-Scramble-Game/Word-Scramble-Game.py`  
**Target Function:** `clear` (line 82)  

---

## 1. Source Fixture Preconditions & Line References

In `games/Word-Scramble-Game/Word-Scramble-Game.py`:

- **Fixture 1 (`note = []`):** Line 276
  - Context: Inside `play_round()`:
    ```python
    274:             clear()
    275:             header(round_num, score + earned, lives, difficulty)
    276:             note = []
    277:             if hint_used:    note.append("hint used: −½ pts")
    278:             if speed_bonus:  note.append("speed bonus: +½ pts")
    279:             note_str = f"  ({', '.join(note)})" if note else ""
    ```
- **Fixture 2 (`valid_words = []`):** Line 345
  - Context: Inside `main()` game round setup:
    ```python
    344:         while lives > 0 and still_playing:
    345:             valid_words = []
    346:             
    347:             for category, words in WORD_BANK.items():
    ```

---

## 2. Literal Test Inputs & Independently Calculated Expected Outputs

Before modifying any implementation, expected outputs were derived independently from the specification and contract requirements:

### Test A: Smallest Valid Input
- **Fixture Reference:** Empty list initialization at line 276 (`note = []`) and line 345 (`valid_words = []`).
- **Literal Input:** `[]`
- **Initial State:** `len == 0`, `input == []`
- **Independently Calculated Expected Return:** `None`
- **Independently Calculated Expected Mutated State:** `[]` (length 0, unchanged empty list)
- **Mutation Verification:** Mutates in-place (remains `[]`), separate check confirms no elements added or modified.

### Test B: Ordinary Input
- **Fixture Reference:** Appending round summary notes to `note` at lines 277–278.
- **Literal Input:** `["hint used: −½ pts", "speed bonus: +½ pts"]`
- **Initial State:** `len == 2`, `input == ["hint used: −½ pts", "speed bonus: +½ pts"]`
- **Independently Calculated Expected Return:** `None`
- **Independently Calculated Expected Mutated State:** `[]` (length 0, all elements emptied)
- **Mutation Verification:** Input list object mutated in-place from 2 elements to 0 elements (`input == []`).

### Test C: Repeated-Value / Domain Boundary Input
- **Fixture Reference:** Duplicate round note entries, or duplicate category-words tuples as seen in `valid_words` (line 345).
- **Literal Input 1 (Repeated Strings):** `["hint used: −½ pts", "hint used: −½ pts"]`
- **Initial State:** `len == 2`, duplicate string elements
- **Independently Calculated Expected Return:** `None`
- **Independently Calculated Expected Mutated State:** `[]`
- **Mutation Verification:** All duplicate elements cleared in-place; resulting list is empty `[]`.
- **Literal Input 2 (Domain Boundary - Nested Structured Tuples):** `[("🐾 Animals", ["cat", "dog"]), ("🐾 Animals", ["cat", "dog"])]`
- **Initial State:** `len == 2`, duplicate `(category, words)` tuples mirroring `valid_words` structure
- **Independently Calculated Expected Return:** `None`
- **Independently Calculated Expected Mutated State:** `[]`
- **Mutation Verification:** Clears collection of complex domain objects in-place to `[]`.

### Test D: Public Interface Preservation (No-Arg Invocation)
- **Fixture Reference:** Call sites at lines 155, 178, 219, 225, 249, 274, 291, 312: `clear()`.
- **Literal Input:** None (0 arguments)
- **Independently Calculated Expected Return:** `None`
- **Expected Side Effect:** Calls `os.system` with `"cls"` on Windows (`nt`) or `"clear"` on POSIX platforms.
