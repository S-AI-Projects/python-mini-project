# R26-T040: Quick-Sort Regression Testing & Mutation Analysis

## 1. Target Interface & Contract
Function: `quick_sort(arr: list[int], reverse: bool = False) -> list[int]` in `math/Quick-Sort/Quick-Sort.py`.

### Contract Invariants:
1. **Ordering:** When `reverse=False`, elements in the result are monotonically non-decreasing ($r_0 \le r_1 \le \dots \le r_{n-1}$). When `reverse=True`, elements are monotonically non-increasing.
2. **Multiplicity Preservation:** The multiset of elements in the output is identical to the input ($\text{multiset}(r) = \text{multiset}(arr)$).
3. **Immutability Contract:** The input list `arr` is never mutated in place. A distinct, newly allocated list is returned.
4. **Boundary Support:** Correctly handles empty list `[]`, single-element lists `[x]`, duplicates `[2, 2, 1]`, already sorted lists, and reversed lists.

---

## 2. Plausible One-Line Mutation

### The Defect
In line 34 of `math/Quick-Sort/Quick-Sort.py`:
- **Original Code:**
  ```python
  if not reverse and value <= pivot:
      left.append(value)
  elif not reverse and value > pivot:
      right.append(value)
  ```
- **Mutant Code (Plausible Developer Error):**
  ```python
  if not reverse and value >= pivot:   # MUTATION: '>=' instead of '<='
      left.append(value)
  elif not reverse and value < pivot:
      right.append(value)
  ```

### Why It Is Plausible:
A developer refactoring or typing Quick Sort partition logic may invert the relational operator (`>=` instead of `<=`), causing greater elements to be partitioned to the left rather than the right.

---

## 3. Minimal Differentiating Fixture & Failure Mechanism

### Reduced Input:
`arr = [2, 2, 1]`

### Expected Output:
`[1, 2, 2]`

### Execution Trace Comparison:

| Step | Original (`<=`) | Mutant (`>=`) |
|:---|:---|:---|
| **Pass 1:** `pivot = arr[-1] = 1`, `arr[:-1] = [2, 2]` | Both values ($2 > 1$) go to `right`. `left = []`, `right = [2, 2]`. | Both values ($2 \ge 1$) go to `left`. `left = [2, 2]`, `right = []`. |
| **Pass 2:** Recursive call on `[2, 2]` | `pivot = 2`, `arr[:-1] = [2]`. $2 \le 2 \implies left = [2]$. Returns `[2, 2]`. | `pivot = 2`, `arr[:-1] = [2]`. $2 \ge 2 \implies left = [2]$. Returns `[2, 2]`. |
| **Combine:** | `left + [1] + right = [] + [1] + [2, 2] = [1, 2, 2]` ✅ | `left + [1] + right = [2, 2] + [1] + [] = [2, 2, 1]` ❌ |

### Named Assertion:
`TestQuickSortFixtures.test_duplicates_multiplicity_preserved`
- **Original:** PASSES (`assert [1, 2, 2] == [1, 2, 2]`)
- **Mutant:** FAILS with `AssertionError: assert [2, 2, 1] == [1, 2, 2]` because elements greater than or equal to pivot are partitioned leftwards, inverting the sorted order.
