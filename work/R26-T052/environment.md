# Environment Documentation

**Task ID:** R26-T052  
**Date:** 2026-11-22  
**Student:** Rhea Sharma  
**Repository:** https://github.com/S-AI-Projects/python-mini-project  
**Branch:** `R26-T052` (format: `student/e26b07f0899/R26-T052`)  

---

## 1. Runtime & Environment Versions

- **Operating System:** macOS (Darwin 24.3.0, arm64)
- **Python Version:** 3.15.2 (`/Library/Frameworks/Python.framework/Versions/3.15/bin/python3`)
- **Standard Library Modules Used:**
  - `unittest` (standard test runner)
  - `unittest.mock` (`patch`)
  - `io.StringIO` (stdout capture)
  - `importlib.util` (dynamic module loader)
  - `os`, `sys`, `pathlib.Path`
- **Git Version:** git 2.39.5 (Apple Git-154)

---

## 2. Test Commands Executed

Focused regression test runner:
```bash
python3 work/R26-T052/check.py
```

Standard library test runner:
```bash
python3 -m unittest tests/test_number_guessing_game.py -v
```

Bytecode syntax compilation check:
```bash
python3 -m py_compile games/Number-Guessing-Game/Number-Guessing-Game.py tests/test_number_guessing_game.py work/R26-T052/check.py
```

---

## 3. Project Test Configuration

The repository uses `pytest` and `unittest` for automated test suites under `tests/`.
- Tests are placed in `tests/test_number_guessing_game.py`.
- Tests inherit from `unittest.TestCase` and mock external I/O, ensuring deterministic execution under both `python3 -m unittest` and `pytest`.
