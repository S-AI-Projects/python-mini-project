# 🎓 GPA Calculator

A clean, beginner-friendly Python utility to calculate credit-weighted Grade Point Average (GPA) with dual-method independent reference comparison.

---

## 🌟 Overview

The **GPA Calculator** calculates credit-weighted GPA from standard or custom grade scales. It incorporates dual-method reference verification, validating the standard quality-point formula against an independent unrolled unit-weight accumulator.

---

## 🚀 How to Run

### 1. Interactive CLI
Run the calculator directly from your terminal:

```bash
python utilities/GPA-Calculator/main.py
```

### 2. Run Tests
Execute the unit test suite:

```bash
python3 -m unittest discover -s utilities/GPA-Calculator -p "test_*.py"
```

---

## 📖 Supported Limits & Validation

- **Standard 4.0 Scale:**
  - `A+`: 4.0, `A`: 4.0, `A-`: 3.7
  - `B+`: 3.3, `B`: 3.0, `B-`: 2.7
  - `C+`: 2.3, `C`: 2.0, `C-`: 1.7
  - `D+`: 1.3, `D`: 1.0, `F`: 0.0
- **Supported Course Inputs:**
  - Sequence of tuples: `[("A", 3), ("B", 1)]`
  - Sequence of dictionaries: `[{"grade": "A", "credits": 3}, {"grade": "B", "credits": 1}]`
- **Enforced Constraints:**
  - Total credits must be strictly greater than `0` (zero total credits rejected with `ValueError`).
  - Unknown letter grades not in the active scale are rejected with `ValueError`.
  - Negative credit values are rejected with `ValueError`.

---

## 🎯 Input & Output Example

### Stated Contract Example:
For 2 courses:
- Course 1: Grade **A** (4.0 points) for **3** credits
- Course 2: Grade **B** (3.0 points) for **1** credit

**Calculation:**
$$\text{Total Quality Points} = (4.0 \times 3) + (3.0 \times 1) = 12.0 + 3.0 = 15.0$$
$$\text{Total Credits} = 3 + 1 = 4.0$$
$$\text{GPA} = \frac{15.0}{4.0} = 3.75$$

**Output:**
```text
Total Courses Entered : 2
Total Credits Earned  : 4.0
Primary Calculated GPA: 3.75
Independent Reference : 3.75
Verification Status   : ✅ MATCHED (100% verified)
```

---

## 🔬 Independent Reference Comparison Focus

The module includes two distinct calculation engines:
1. `calculate_gpa`: The primary credit-weighted formula.
2. `calculate_gpa_reference`: An independent table accumulator.
3. `verify_gpa_with_reference`: Computes both and asserts consistency within $10^{-4}$ tolerance, ensuring verification failures are triggered if any calculation discrepancy occurs.
