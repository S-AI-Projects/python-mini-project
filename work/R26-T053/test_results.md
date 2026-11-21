# Test Results Documentation

**Task ID:** R26-T053  
**Target:** `games/Pygame-Chess/main.py` -> `main` (line 9)  
**Test Runner:** `work/R26-T053/check.py`  

---

## 1. Source Preconditions & Line References

In `games/Pygame-Chess/main.py`:
- `main()` definition: line 9
- Initial draw: line 18 (`renderer.draw(screen)`)
- Loop start: line 21 (`while running:`)
- Event poll: line 23 (`for event in pygame.event.get():`)
- Quit event: line 25 (`if event.type == pygame.QUIT: running = False`)
- Mouse click: line 28 (`elif event.type == pygame.MOUSEBUTTONDOWN:`)
- Game active guard: lines 30 & 34 (`if not board.game_over():`)
- Mouse handler dispatch: line 32 (`input_handler.get_mouse_pos()`)
- AI move trigger: line 35 (`ai.computer_move()`)
- Frame render: line 37 (`renderer.draw(screen)`)
- Game over termination: lines 39–41 (`if board.game_over(): pygame.time.wait(5000); running = False`)

---

## 2. Test Execution Summary

Command:
```bash
python3 work/R26-T053/check.py
```

- **Top-Level Tests Executed:** 3
- **Oracle Subtests Executed:** 21
- **Passed:** 3 (all 21 subtests passed)
- **Failures:** 0
- **Errors:** 0
- **Exit Code:** 0

---

## 3. Detailed Results & Oracle Comparison

### Test 1: Smallest Valid Input Domain (`[QUIT]`)
- **Input:** Single `pygame.QUIT` event.
- **Oracle Prediction:**
  - `return_value`: `None`
  - `draw_count`: `2` (1 initial + 1 frame)
  - `mouse_handler_count`: `0`
  - `ai_move_count`: `0`
  - `wait_called`: `False`
  - `terminated`: `True`
- **Actual Result:** Matches oracle exactly. **PASS**

### Test 2: Ordinary Input (`[MOUSEBUTTONDOWN, QUIT]`)
- **Input:** Single click followed by quit.
- **Oracle Prediction:**
  - `return_value`: `None`
  - `draw_count`: `2`
  - `mouse_handler_count`: `1`
  - `ai_move_count`: `1`
  - `wait_called`: `False`
  - `terminated`: `True`
- **Actual Result:** Matches oracle exactly. **PASS**

### Test 3: 21 Enumerated Inputs vs Oracle
All 21 enumerated event streams (immediate quit, non-interactive key/mouse events, multi-click sequences, click-triggered game over, and initial game over) produced traces identical to the independent oracle model `ChessMainOracle`. **PASS**

---

## 4. Failure Propagation Verification

When an assertion failure is triggered, `work/R26-T053/check.py` prints the traceback and exits with a non-zero exit code (`sys.exit(1)`).
