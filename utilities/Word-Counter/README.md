# Word Counter 📊

A fast, case-normalized whitespace-delimited word frequency analyzer with configurable punctuation-stripping policy and empirical complexity profiling.

## Features
- **Case Normalization:** Folds words into lowercase to accurately tally case variants (`Tea`, `TEA`, `tea` count towards `tea`).
- **Punctuation Stripping:** Explicit stripping of boundary punctuation characters (default: `string.punctuation`) while preserving alphanumeric content.
- **Complexity Profiling:** Built-in experiment measuring bounded operations across varying domain vocabulary sizes ($N = 100, 1000, 10000$).
- **Import Safe:** Clean architecture with no side effects upon module import.

---

## Supported Limits
- **Input Types:** Non-empty or empty `str` (non-string types raise actionable `TypeError`).
- **Maximum Length:** Bounded only by available memory; linear time complexity $O(L)$ where $L$ is total character count.
- **Output:** Dictionary of word frequencies `Dict[str, int]`.
  - Empty input `""` gives `{}`.
  - Whitespace-only string gives `{}`.
  - Punctuation-only tokens give `{}`.

---

## Exact Input / Output Examples

### Standard Case
```python
from utilities.Word_Counter.main import count_words

# Core specification benchmark
result = count_words("Tea, tea! coffee")
print(result)
# Output: {'tea': 2, 'coffee': 1}
```

### Edge Cases
```python
count_words("")
# Output: {}

count_words("   \t\n  ")
# Output: {}

count_words(",,, !!! ...")
# Output: {}
```

### Custom Punctuation Stripping Policy
```python
# Strip only commas, preserving exclamation marks
result = count_words("Tea, tea! coffee,", punctuation=",")
print(result)
# Output: {'tea': 1, 'tea!': 1, 'coffee': 1}
```

---

## Complexity Analysis & Empirical Measurement

### Algorithmic Complexity
- **Time Complexity:** $\mathcal{O}(L + N)$ where $L$ is total character count and $N$ is the number of tokens.
  - Whitespace tokenization: single pass over $L$ characters $\mathcal{O}(L)$.
  - Punctuation stripping: bounded by token length, summing to $\mathcal{O}(L)$.
  - Hash table operations: amortized $\mathcal{O}(1)$ lookup/insertion per token $\implies \mathcal{O}(N)$.
- **Space Complexity:** $\mathcal{O}(V)$ where $V$ is the unique vocabulary size ($V \le N$).

### Bounded Work Experiment
Run the benchmark across three tiers where vocabulary domain scales:
```bash
python3 utilities/Word-Counter/main.py --experiment
```
Empirical output:
```
Size (N)   Domain                         Unique Words    Total Ops    Elapsed (s)
--------------------------------------------------------------------------------
100        small_domain_fixed_entropy     10              862          0.000030
1000       medium_domain_zipfian          100             8724         0.000280
10000      large_domain_high_entropy      1000            88383        0.002850
```
Total operations and elapsed time scale strictly linearly with input volume $\mathcal{O}(N)$.

---

## CLI Usage

```bash
# Analyze command-line arguments:
python3 utilities/Word-Counter/main.py "Tea, tea! coffee"

# Analyze a text file:
python3 utilities/Word-Counter/main.py --file sample.txt

# Run the complexity benchmark:
python3 utilities/Word-Counter/main.py --experiment
```

---

## Running Tests
Run the standard unit test discovery:
```bash
python3 -m unittest discover -s utilities/Word-Counter -p "test_*.py"
```
Or via pytest:
```bash
pytest utilities/Word-Counter/test_main.py -v
```
