# Task R26-T034: Invariant Justification for `main` (`utilities/multithreaded_scraper/main.py`)

## 1. Target Function Contract
```python
def main(argv=None)
```
- **Target Location**: `utilities/multithreaded_scraper/main.py` (lines 10–56).
- **Public Inputs**:
  - `argv` (`list[str] | None`): Optional CLI arguments list. If `None`, arguments are parsed from `sys.argv[1:]`.
- **Return Value**:
  - `None`. Execution terminates cleanly without unhandled exception.
- **External Dependencies & Mocking**:
  - HTTP requests via `MultithreadedScraper._fetch_url` are mocked to return deterministic HTML content (`CONTROLLED_HTML`), isolating execution from external network state.
  - File exports are written into sandboxed temporary directories (`tempfile.TemporaryDirectory`).

---

## 2. Invariants Established & Justified

### Invariant 1: Output Type & Return Value Invariance
- **Statement**: Calling `main(argv)` always yields return value `None` and finishes cleanly.
- **Preconditions**: Valid CLI arguments and reachable target URLs.
- **Justification**: A CLI entrypoint contract defines exit without uncaught exceptions for valid input combinations.

### Invariant 2: Output Shape & Schema Invariance
- **Statement**: The exported file (JSON or CSV) adheres strictly to the documented scraper schema:
  - Required fields per scraped item: `url`, `title`, `meta_description`, `headings`, `links`, and `depth`.
- **Preconditions**: Line 49–54 (`DataExporter` calls).
- **Justification**: Downstream data consumers depend on predictable record keys.

### Invariant 3: Input-Mutation Invariance
- **Statement**: `argv` before calling `main(argv)` is identical in contents, ordering, and length to `argv` after invocation:
  $$\text{argv}_{\text{before}} == \text{argv}_{\text{after}}$$
- **Preconditions**: Lines 10–21 (argument parsing).
- **Justification**: Caller argument lists must remain immutable to prevent subtle bugs in test harnesses or embedding workflows.

### Invariant 4: Fresh Equivalent Inputs Invariance
- **Statement**: For any two distinct, identical input vectors $\text{argv}_A$ and $\text{argv}_B$ executed under identical mock network responses:
  $$\text{output}(\text{argv}_A) \equiv \text{output}(\text{argv}_B)$$
- **Preconditions**: Lines 36–54 (deterministic pipeline execution).
- **Justification**: Guarantees reproducibility and absence of hidden mutable global state between consecutive runs.

---

## 3. Property Generator Specification
- **Seed**: Fixed PRNG seed `random.Random(42)`.
- **Bounded Domain**:
  - URLs: Sampled from 25 valid HTTP/HTTPS URLs.
  - Workers: Bounded integer $w \in [1, 4]$.
  - Depth: Bounded integer $d \in [1, 2]$.
  - Delay: Controlled float $0.0$.
  - Output formats: Uniform choice between `"json"` and `"csv"`.
- **Cases Tested**: 100 consecutive valid runs, all asserting all 4 invariants.
