# Test Results for Task R26-T047

- Python: 3.15.2 (main, Oct 25 2026, 16:57:51) [Clang 21.0.0 (clang-2100.3.34.2)]
- Tests executed: Executable worked example tests for `Projectile-Motion-Game.py`
- Total tests run in suite: 4
- Anchor preconditions verified: `GRAVITY = 9.81` (line 14)

## Test Cases

| Test | Input / Fixture | Expected | Actual | Status |
| --- | --- | --- | --- | --- |
| Precondition anchor GRAVITY | GRAVITY | 9.81 | 9.81 | PASS |
| Smallest valid input (1.0 m/s, 1.0 deg) | speed=1.0, angle=1.0 | TOF=0.00s, Hmax=0.00m, Range=0.00m | TOF=0.00s, Hmax=0.00m, Range=0.00m | PASS |
| Ordinary worked example (10.0 m/s, 45.0 deg) | speed=10.0, angle=45.0 | TOF=1.44s, Hmax=2.55m, Range=10.19m | TOF=1.44s, Hmax=2.55m, Range=10.19m | PASS |
| main() CLI execution check | Interactive input ['1', '10', '45', '2'] | TOF=1.44s, Hmax=2.55m, Range=10.19m | Matched formatted results in stdout | PASS |
