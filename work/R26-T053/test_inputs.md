# Test Inputs and Independently Calculated Expected Outputs

**Task ID:** R26-T053  
**Target File:** `games/Pygame-Chess/main.py`  
**Target Function:** `main` (line 9)  

---

## 1. Source Preconditions & Line References

In `games/Pygame-Chess/main.py`:
- **Line 9 (`def main():`):** Entrypoint for Pygame Chess game loop.
- **Line 10 (`pygame.init()`):** Initializes pygame subsystems.
- **Line 11 (`screen = pygame.display.set_mode((720, 720))`):** Initializes display surface with dimension 720x720.
- **Line 18 (`renderer.draw(screen)`):** Initial board render prior to entering event loop.
- **Line 20 (`running = True`):** Loop guard variable initialized to True.
- **Line 21 (`while running:`):** Main game execution loop.
- **Line 23 (`for event in pygame.event.get():`):** Event consumer queue.
- **Line 25 (`if event.type == pygame.QUIT:`):** Handles application quit, sets `running = False`.
- **Line 28 (`elif event.type == pygame.MOUSEBUTTONDOWN:`):** Handles player mouse input.
- **Lines 30 & 34 (`if not board.game_over():`):** Guard conditions ensuring actions only occur when board is active.
- **Line 32 (`input_handler.get_mouse_pos()`):** Processes square selection or player move.
- **Line 35 (`ai.computer_move()`):** Triggers black AI move when game remains active.
- **Line 37 (`renderer.draw(screen)`):** Renders updated board state on each loop frame.
- **Lines 39–41 (`if board.game_over(): pygame.time.wait(5000); running = False`):** Terminal game state handler.

---

## 2. Fixture Preconditions: Smallest and Ordinary Inputs

### Smallest Valid Input (Immediate Quit)
- **Precondition Reference:** Line 25 (`if event.type == pygame.QUIT: running = False`)
- **Literal Input:** `[Event(type=pygame.QUIT)]`
- **Independently Calculated Expected Output:**
  - Return Value: `None`
  - Output Type: `NoneType`
  - Render Draw Calls: `2` (1 before loop at line 18, 1 inside loop at line 37)
  - Input Handler Calls: `0`
  - AI Move Calls: `0`
  - Wait Calls: `0`
  - Loop Terminated: `True`

### Ordinary Input (Player Click + AI Response + Quit)
- **Precondition Reference:**
  - Line 28 (`elif event.type == pygame.MOUSEBUTTONDOWN:`)
  - Line 32 (`input_handler.get_mouse_pos()`)
  - Line 35 (`ai.computer_move()`)
  - Line 25 (`if event.type == pygame.QUIT: running = False`)
- **Literal Input:** `[Event(type=pygame.MOUSEBUTTONDOWN), Event(type=pygame.QUIT)]`
- **Independently Calculated Expected Output:**
  - Return Value: `None`
  - Output Type: `NoneType`
  - Render Draw Calls: `2`
  - Input Handler Calls: `1`
  - AI Move Calls: `1`
  - Wait Calls: `0`
  - Loop Terminated: `True`

---

## 3. Enumeration of 21 Small Valid Inputs for Oracle Comparison

1. `Input 1`: `[QUIT]` -> Immediate termination.
2. `Input 2`: `[KEYDOWN, QUIT]` -> Ignored non-interactive event then quit.
3. `Input 3`: `[KEYUP, QUIT]` -> Ignored keyboard release then quit.
4. `Input 4`: `[MOUSEMOTION, QUIT]` -> Ignored mouse movement then quit.
5. `Input 5`: `[ACTIVEEVENT, QUIT]` -> Ignored window focus change then quit.
6. `Input 6`: `[VIDEORESIZE, QUIT]` -> Ignored window resize then quit.
7. `Input 7`: `[USEREVENT, QUIT]` -> Ignored user custom event then quit.
8. `Input 8`: `[MOUSEBUTTONDOWN, QUIT]` -> Single click, AI move, then quit.
9. `Input 9`: `[MOUSEBUTTONDOWN, MOUSEBUTTONDOWN, QUIT]` -> Two clicks (select + move) then quit.
10. `Input 10`: `[MOUSEBUTTONDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONDOWN, QUIT]` -> Three clicks then quit.
11. `Input 11`: `[MOUSEBUTTONDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONDOWN, QUIT]` -> Four clicks then quit.
12. `Input 12`: `[KEYDOWN, MOUSEBUTTONDOWN, QUIT]` -> Keydown followed by click then quit.
13. `Input 13`: `[MOUSEMOTION, MOUSEBUTTONDOWN, QUIT]` -> Motion followed by click then quit.
14. `Input 14`: `[MOUSEBUTTONDOWN, KEYDOWN, QUIT]` -> Click followed by keydown then quit.
15. `Input 15`: `[MOUSEBUTTONDOWN, MOUSEMOTION, QUIT]` -> Click followed by motion then quit.
16. `Input 16`: `[MOUSEBUTTONDOWN, MOUSEBUTTONDOWN, KEYDOWN, QUIT]` -> Two clicks followed by keydown then quit.
17. `Input 17`: `[KEYDOWN, KEYUP, MOUSEBUTTONDOWN, QUIT]` -> Multiple ignored events then click then quit.
18. `Input 18`: `[MOUSEBUTTONDOWN, USEREVENT, QUIT]` -> Click followed by custom event then quit.
19. `Input 19`: `[MOUSEBUTTONDOWN]` with `board.game_over()=True` on click -> Terminal state triggers `pygame.time.wait(5000)` and terminates.
20. `Input 20`: `[]` with initial `board.game_over()=True` -> Immediate game over triggers `pygame.time.wait(5000)` and terminates.
21. `Input 21`: `[QUIT, MOUSEBUTTONDOWN]` -> Loop terminates at quit; subsequent event is ignored.
