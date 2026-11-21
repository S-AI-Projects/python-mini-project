# Task R26-T035: Repeatability and State Isolation for `is_prime` (`math/Prime-Number-Analyzer/Prime-Number-Analyzer.py`)

## 1. Function Contract & Observable Dependencies

### Signature
```python
def is_prime(num: int) -> bool:
```
- **Target Location**: `math/Prime-Number-Analyzer/Prime-Number-Analyzer.py` (lines 12–23).
- **Public Inputs**:
  - `num` (`int`): Integer to test for primality.
- **Return Value**:
  - `bool`: `True` if `num` is prime, `False` otherwise.
- **Mutation Behavior**:
  - Strictly pure: No mutation of the input parameter, no mutation of global or module state.
- **Observable Dependencies**:
  - **Explicit Statement**: `is_prime` has **ZERO** external observable dependencies.
  - It does not access the filesystem, network, system clock/time, random number generators, thread locals, or GUI elements.
  - Relies solely on standard deterministic arithmetic and `math.sqrt`.

---

## 2. Fixture & Domain Partitions

The test fixture uses the domain around **1, 2, 9, and 11**:
- **Domain around 1:**
  - $0 \to \text{False}$ (Line 14)
  - $1 \to \text{False}$ (Line 14)
- **Domain around 2:**
  - $2 \to \text{True}$ (Line 16, smallest prime and only even prime)
  - $3 \to \text{True}$ (Line 23)
  - $4 \to \text{False}$ (Line 18, even composite)
- **Domain around 9:**
  - $8 \to \text{False}$ (Line 18)
  - $9 \to \text{False}$ (Line 21, smallest odd composite divisible by 3)
  - $10 \to \text{False}$ (Line 18)
- **Domain around 11:**
  - $11 \to \text{True}$ (Line 23)
  - $12 \to \text{False}$ (Line 18)
  - $13 \to \text{True}$ (Line 23)

---

## 3. Sieve through 12 (Exclusive Upper-Bound)
- Interface requirement: Sieve through 12 with exclusive upper bound $\to \text{range}(2, 12)$.
- Primes in range: $[2, 3, 5, 7, 11]$.
- Non-primes in range: $[4, 6, 8, 9, 10]$.

---

## 4. Verification Repeatability Protocol
- **Run 1 (Fresh State):**
  $\text{is\_prime}([1, 2, 9, 11]) \to [\text{False}, \text{True}, \text{False}, \text{True}]$
- **Run 2 (Fresh State Re-evaluation):**
  $\text{is\_prime}([1, 2, 9, 11]) \to [\text{False}, \text{True}, \text{False}, \text{True}]$
- **Interleaved Execution:**
  Evaluating arbitrary inputs $[997, 100, 17, 49]$ between runs.
- **Run 3 (Post-Interleaving):**
  $\text{is\_prime}([1, 2, 9, 11]) \to [\text{False}, \text{True}, \text{False}, \text{True}]$
- **Conclusion:** $\text{Run}_1 \equiv \text{Run}_2 \equiv \text{Run}_3$, confirming complete independence from prior invocations.
