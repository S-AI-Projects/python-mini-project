# R26-T036: Refactoring `_build_namespace` — Extract `_base_math_names`

## Target

`_build_namespace` in `math/Scientific-Graphing-Calculator/Scientific-Graphing-Calculator.py`

## What Changed

**Before (lines 23-27):** `_build_namespace` mixed two responsibilities:
1. Building the base math namespace (filtering `vars(math)`, adding `abs`/`round`)
2. Conditionally enriching it with numpy ufuncs and `x`

**After:** Responsibility #1 is extracted into `_base_math_names()`, a pure function
that returns the standard math namespace dict. `_build_namespace` now calls it and
only handles the numpy/x enrichment.

## Why This Is Clearer

| Aspect | Before | After |
|--------|--------|-------|
| Name | Unnamed inline dict comprehension + two assignments | `_base_math_names()` — name explains intent |
| Testability | Must test via `_build_namespace` | Can test the base namespace independently |
| Single responsibility | Mixed base + numpy override | Each function does one thing |

## What Is Preserved

- Return type: `dict`
- Key set: identical for both `x_val=None` and `x_val=<value>` cases
- Ordering: dict insertion order unchanged
- Side effects: none (both before and after)
- Public arguments: `_build_namespace(x_val=None)` unchanged
- Algorithm: same dict comprehension, same filter, same override logic

## Source Anchors

- `_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}` (line 17)
- `history = []` (line 102, in `main()`)
