# Test Results for Task R26-T043

- Python: 3.15.2 (main, Oct 25 2026, 16:57:51) [Clang 21.0.0 (clang-2100.3.34.2)]
- Tests executed: `solve_quadratic` cross-check against 21 independent reference cases
- Total tests run in suite: 4
- Precondition verified: a == 0 raises ValueError (line 24)

## Reference Comparison Cases

| Case | Input (a, b, c) | Expected (kind, r1, r2, d) | Actual (kind, r1, r2, d) | Status |
| --- | --- | --- | --- | --- |
| 1 | (1, 0, 0) | (repeated_real, 0.0, 0.0, d=0.0) | (repeated_real, 0.0, 0.0, d=0) | PASS |
| 2 | (1, -3, 2) | (distinct_real, 2.0, 1.0, d=1.0) | (distinct_real, 2.0, 1.0, d=1) | PASS |
| 3 | (1, -5, 6) | (distinct_real, 3.0, 2.0, d=1.0) | (distinct_real, 3.0, 2.0, d=1) | PASS |
| 4 | (1, 0, -1) | (distinct_real, 1.0, -1.0, d=4.0) | (distinct_real, 1.0, -1.0, d=4) | PASS |
| 5 | (1, 5, 6) | (distinct_real, -2.0, -3.0, d=1.0) | (distinct_real, -2.0, -3.0, d=1) | PASS |
| 6 | (2, -5, 2) | (distinct_real, 2.0, 0.5, d=9.0) | (distinct_real, 2.0, 0.5, d=9) | PASS |
| 7 | (1, -2, 1) | (repeated_real, 1.0, 1.0, d=0.0) | (repeated_real, 1.0, 1.0, d=0) | PASS |
| 8 | (1, 2, 1) | (repeated_real, -1.0, -1.0, d=0.0) | (repeated_real, -1.0, -1.0, d=0) | PASS |
| 9 | (1, -4, 4) | (repeated_real, 2.0, 2.0, d=0.0) | (repeated_real, 2.0, 2.0, d=0) | PASS |
| 10 | (1, 4, 4) | (repeated_real, -2.0, -2.0, d=0.0) | (repeated_real, -2.0, -2.0, d=0) | PASS |
| 11 | (4, -4, 1) | (repeated_real, 0.5, 0.5, d=0.0) | (repeated_real, 0.5, 0.5, d=0) | PASS |
| 12 | (1, 0, 1) | (complex, 1j, (-0-1j), d=-4.0) | (complex, 1j, -1j, d=-4) | PASS |
| 13 | (1, 0, 4) | (complex, 2j, (-0-2j), d=-16.0) | (complex, 2j, -2j, d=-16) | PASS |
| 14 | (1, -2, 2) | (complex, (1+1j), (1-1j), d=-4.0) | (complex, (1+1j), (1-1j), d=-4) | PASS |
| 15 | (1, 2, 2) | (complex, (-1+1j), (-1-1j), d=-4.0) | (complex, (-1+1j), (-1-1j), d=-4) | PASS |
| 16 | (-1, 3, -2) | (distinct_real, 1.0, 2.0, d=1.0) | (distinct_real, 1.0, 2.0, d=1) | PASS |
| 17 | (-1, 2, -1) | (repeated_real, 1.0, 1.0, d=0.0) | (repeated_real, 1.0, 1.0, d=0) | PASS |
| 18 | (1, -2, -8) | (distinct_real, 4.0, -2.0, d=36.0) | (distinct_real, 4.0, -2.0, d=36) | PASS |
| 19 | (1, -6, 5) | (distinct_real, 5.0, 1.0, d=16.0) | (distinct_real, 5.0, 1.0, d=16) | PASS |
| 20 | (2, 1, -3) | (distinct_real, 1.0, -1.5, d=25.0) | (distinct_real, 1.0, -1.5, d=25) | PASS |
| 21 | (2, 0, 8) | (complex, 2j, (-0-2j), d=-64.0) | (complex, 2j, -2j, d=-64) | PASS |
