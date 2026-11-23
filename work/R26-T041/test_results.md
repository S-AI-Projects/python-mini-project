# Test Results for Task R26-T041

- Python: 3.15.2 (main, Oct 25 2026, 16:57:51) [Clang 21.0.0 (clang-2100.3.34.2)]
- Tests executed: `collatz_next` contract and regression tests
- Total tests run in suite: 4

## Test Cases

| Test | Input | Expected | Actual | Precondition / Anchor | Status |
| --- | --- | --- | --- | --- | --- |
| Smallest valid input (n=1) | 1 | 4 | 4 | steps_cache = {1: 0} at line 6 | PASS |
| Ordinary odd input (n=3) | 3 | 10 | 10 | odd formula 3*n + 1 near line 8 | PASS |
| Ordinary even input (n=4) | 4 | 2 | 2 | even formula n // 2 near line 8 | PASS |
| Ordinary odd input (n=5) | 5 | 16 | 16 | odd formula 3*n + 1 near line 8 | PASS |
| Ordinary even input (n=6) | 6 | 3 | 3 | even formula n // 2 near line 8 | PASS |
| Boundary cycle input (n=2) | 2 | 1 | 1 | even formula n // 2 near line 8 | PASS |
| Mutation check | steps_cache | {1: 0} | {1: 0} | steps_cache = {1: 0} (line 6) | PASS |
