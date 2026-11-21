# Independent Reference Oracle & Result Table

**Task ID:** R26-T053  
**Target:** `games/Pygame-Chess/main.py` -> `main`  

---

## 1. Specification of the Independent Reference Oracle

The oracle is an independent, pure state-machine simulation of the game loop contract. It does NOT invoke `games/Pygame-Chess/main.py`.

```python
class ChessMainOracle:
    """Independent reference oracle for games/Pygame-Chess/main.py loop domain."""

    def __init__(self):
        pass

    def evaluate(self, event_stream, initial_game_over=False, game_over_after_clicks=None):
        draw_count = 1  # Line 18: initial renderer.draw(screen) before while loop
        mouse_handler_count = 0
        ai_move_count = 0
        wait_called = False
        terminated = False
        game_over = initial_game_over

        running = True
        event_idx = 0

        while running:
            # Check terminal game over condition from prior actions
            if game_over:
                wait_called = True
                running = False
                terminated = True
                draw_count += 1
                break

            # Process event stream batch
            if event_idx < len(event_stream):
                event = event_stream[event_idx]
                event_idx += 1

                if event == "QUIT":
                    running = False
                    terminated = True
                elif event == "MOUSEBUTTONDOWN":
                    if not game_over:
                        mouse_handler_count += 1
                        if game_over_after_clicks is not None and mouse_handler_count >= game_over_after_clicks:
                            game_over = True
                        if not game_over:
                            ai_move_count += 1
                # Ignored events (KEYDOWN, MOUSEMOTION, etc.) pass without effect
            else:
                # Event queue exhausted
                running = False
                terminated = True

            draw_count += 1  # Line 37: renderer.draw(screen) in loop body

            if game_over:
                wait_called = True
                running = False
                terminated = True

        return {
            "return_value": None,
            "draw_count": draw_count,
            "mouse_handler_count": mouse_handler_count,
            "ai_move_count": ai_move_count,
            "wait_called": wait_called,
            "terminated": terminated,
        }
```

---

## 2. Reviewed Explicit Result Table Across 21 Inputs

| # | Input Event Sequence | Preconditions | Expected Draws | Expected Mouse | Expected AI | Expected Wait | Expected Return | Terminated |
|---|---|---|---|---|---|---|---|---|
| 1 | `["QUIT"]` | Line 25 | 2 | 0 | 0 | False | `None` | True |
| 2 | `["KEYDOWN", "QUIT"]` | Line 25 | 3 | 0 | 0 | False | `None` | True |
| 3 | `["KEYUP", "QUIT"]` | Line 25 | 3 | 0 | 0 | False | `None` | True |
| 4 | `["MOUSEMOTION", "QUIT"]` | Line 25 | 3 | 0 | 0 | False | `None` | True |
| 5 | `["ACTIVEEVENT", "QUIT"]` | Line 25 | 3 | 0 | 0 | False | `None` | True |
| 6 | `["VIDEORESIZE", "QUIT"]` | Line 25 | 3 | 0 | 0 | False | `None` | True |
| 7 | `["USEREVENT", "QUIT"]` | Line 25 | 3 | 0 | 0 | False | `None` | True |
| 8 | `["MOUSEBUTTONDOWN", "QUIT"]` | Lines 28, 32, 35 | 3 | 1 | 1 | False | `None` | True |
| 9 | `["MOUSEBUTTONDOWN", "MOUSEBUTTONDOWN", "QUIT"]` | Lines 28, 32, 35 | 4 | 2 | 2 | False | `None` | True |
| 10 | 3 x `MOUSEBUTTONDOWN` + `QUIT` | Lines 28, 32, 35 | 5 | 3 | 3 | False | `None` | True |
| 11 | 4 x `MOUSEBUTTONDOWN` + `QUIT` | Lines 28, 32, 35 | 6 | 4 | 4 | False | `None` | True |
| 12 | `["KEYDOWN", "MOUSEBUTTONDOWN", "QUIT"]` | Lines 25, 28 | 4 | 1 | 1 | False | `None` | True |
| 13 | `["MOUSEMOTION", "MOUSEBUTTONDOWN", "QUIT"]` | Lines 25, 28 | 4 | 1 | 1 | False | `None` | True |
| 14 | `["MOUSEBUTTONDOWN", "KEYDOWN", "QUIT"]` | Lines 25, 28 | 4 | 1 | 1 | False | `None` | True |
| 15 | `["MOUSEBUTTONDOWN", "MOUSEMOTION", "QUIT"]` | Lines 25, 28 | 4 | 1 | 1 | False | `None` | True |
| 16 | 2 x `MOUSEBUTTONDOWN` + `KEYDOWN` + `QUIT` | Lines 25, 28 | 5 | 2 | 2 | False | `None` | True |
| 17 | `KEYDOWN` + `KEYUP` + `MOUSEBUTTONDOWN` + `QUIT` | Lines 25, 28 | 5 | 1 | 1 | False | `None` | True |
| 18 | `MOUSEBUTTONDOWN` + `USEREVENT` + `QUIT` | Lines 25, 28 | 4 | 1 | 1 | False | `None` | True |
| 19 | `["MOUSEBUTTONDOWN"]` (causes game_over) | Lines 30, 39 | 2 | 1 | 0 | True | `None` | True |
| 20 | `[]` (initial game_over=True) | Lines 30, 39 | 2 | 0 | 0 | True | `None` | True |
| 21 | `["QUIT", "MOUSEBUTTONDOWN"]` | Line 25 | 2 | 0 | 0 | False | `None` | True |
