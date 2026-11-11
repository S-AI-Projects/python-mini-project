# 💰 Simple Interest Calculator

A robust command-line utility for calculating simple interest using Python's standard library `decimal.Decimal` module to ensure high precision without binary floating-point rounding errors.

---

## 🎯 Purpose

This project provides an exact, reproducible tool for computing simple interest according to the standard financial formula:

$$\text{Simple Interest} = \frac{\text{Principal} \times \text{Rate} \times \text{Years}}{100}$$

Unlike standard float arithmetic, all calculations are performed strictly using `decimal.Decimal` arithmetic. Floats are converted via `Decimal(str(x))` so that values such as `0.1` retain their exact decimal representation.

---

## 📋 Contract & Specifications

### Core Contract Examples
- **Standard calculation**: `1000` at `5%` for `2` years $\rightarrow$ `100`
- **Zero duration**: `years = 0` $\rightarrow$ `0`
- **Negative principal**: `principal < 0` $\rightarrow$ raises `ValueError("Principal cannot be negative")`

### Input Validation & Supported Limits
- **Numeric Precision**: Uses arbitrary-precision `decimal.Decimal` arithmetic.
- **Finite Numbers Only**: Special non-finite values (`NaN`, `Infinity`, `-Infinity`) are rejected with `ValueError`.
- **String Parsing**: Empty strings and non-numeric strings (e.g. `"abc"`, `"$100"`) are rejected with `ValueError`.
- **Strict Typing**: Boolean values (`True`, `False`) and unconvertible types (`list`, `dict`, `None`) are rejected with `TypeError`.
- **Negative Rate & Negative Years**: The task specifies no rule for negative rate or negative years. They are **not restricted by the contract** and are evaluated according to the standard mathematical formula without raising an error.

---

## 🚀 Usage

### 1. Command-Line Arguments Mode
Provide exactly three arguments (`<principal> <rate> <years>`):

```bash
python3 utilities/Simple-Interest-Calculator/main.py 1000 5 2
```
Output:
```text
💰 Simple Interest: 100
```

All results are formatted via `format_currency` without scientific notation (`E+`).

If invalid arguments or negative principal are supplied, the tool prints a descriptive error message and exits with a non-zero exit code:

```bash
python3 utilities/Simple-Interest-Calculator/main.py -100 5 2
```
Output:
```text
❌ Error: Principal cannot be negative
```

### 2. Interactive Mode
Run the script without arguments to enter interactive mode:

```bash
python3 utilities/Simple-Interest-Calculator/main.py
```

Prompts:
```text
💰 Simple Interest Calculator 💰
Calculate simple interest accurately using decimal arithmetic.

🎯 Enter Principal amount: 1000
📊 Enter Annual Interest Rate (%): 5
⏳ Enter Time period (years): 2

✅ Simple Interest: 100
👋 Thanks for using Simple Interest Calculator!
```

---

## 🧪 Running Tests

Run the complete test suite using Python's standard library `unittest`:

```bash
python3 -m unittest discover -s utilities/Simple-Interest-Calculator -p "test_*.py"
```

---

## 🔬 Independent Reference Comparisons

To ensure precision and verify implementation correctness beyond self-testing, the calculation is verified against two independent mathematical references:

1. **Exact Rational Arithmetic (`fractions.Fraction`)**:
   An independent calculation is performed using `fractions.Fraction`:
   $$\text{Interest}_{\text{Fraction}} = \frac{\text{Fraction}(P) \times \text{Fraction}(R) \times \text{Fraction}(T)}{\text{Fraction}(100)}$$
   The exact rational value is verified against the `Decimal` output without importing or relying on `main.py`.

2. **Iterative Whole-Years Accumulation**:
   For integer time periods, an iterative loop computes the annual interest $\frac{P \times R}{100}$ and accumulates it once per whole year across $N$ iterations, confirming agreement with the direct multiplication formula.
