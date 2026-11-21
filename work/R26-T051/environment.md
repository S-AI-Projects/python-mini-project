# Environment Documentation

**Task ID:** R26-T051  
**Date:** 2026-11-22  
**Student:** Rhea Sharma  
**Repository:** https://github.com/S-AI-Projects/python-mini-project  
**Branch:** `student/e26b07f0899`  

---

## 1. Runtime & Tool Versions

- **Operating System:** macOS (Darwin 24.3.0, arm64)
- **Python Version:** 3.15.2 (`/Library/Frameworks/Python.framework/Versions/3.15/bin/python3`)
- **Standard Library Modules Used:**
  - `unittest` (standard test framework)
  - `unittest.mock` (`patch`, `MagicMock`)
  - `importlib.util` (dynamic module loader)
  - `os`, `sys`, `pathlib.Path`
- **Git Version:** git 2.39.5 (Apple Git-154)

---

## 2. Test Command

```bash
python3 work/R26-T051/check.py
```

Alternative standard library runner:
```bash
python3 -m unittest tests/test_word_scramble_clear.py -v
```

---

## 3. Project Test Configuration

The repository specifies `pytest` as the project test runner in `pyproject.toml` and `CONTRIBUTING.md`:
- Test root directory: `tests/`
- Test file naming: `tests/test_*.py`
- Tests written with `unittest.TestCase` are natively compatible with both `pytest` and `python3 -m unittest`.
