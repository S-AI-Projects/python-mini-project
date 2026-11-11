# 🔢 Matrix Determinant Calculator

A robust command-line utility for calculating the determinant of square matrices with rigorous input validation and exact fraction arithmetic.

---

## 🎯 Purpose

This project provides an educational and reliable tool to compute the determinant of $N \times N$ square matrices. It implements an explicit input/output contract, dimensions checking, type validation, and exact calculation for integer matrices using Gaussian elimination.

---

## 📋 Input / Output Contract & Examples

### Supported Inputs
- Square matrices represented as lists of numeric lists: `list[list[int | float]]`.
- Both integer matrices (computed with exact arithmetic) and floating-point matrices are supported.
- Dimensions supported: $1 \times 1$ up to arbitrary $N \times N$ square matrices.

### Exact Contract Examples

1. **$2 \times 2$ Matrix**:
   - **Input**: `[[1, 2], [3, 4]]`
   - **Determinant**: `-2` ($1 \cdot 4 - 2 \cdot 3 = 4 - 6 = -2$)

2. **$1 \times 1$ Matrix**:
   - **Input**: `[[5]]`
   - **Determinant**: `5`

3. **$3 \times 3$ Matrix**:
   - **Input**: `[[6, 1, 1], [4, -2, 5], [2, 8, 7]]`
   - **Determinant**: `-306`

4. **Nonsquare Matrices (Rejected with `ValueError`)**:
   - `[[1, 2, 3], [4, 5, 6]]` ($2 \times 3$) $\to$ `ValueError: Matrix must be square: expected 2 columns, but found row with 3 columns.`
   - `[[1], [2]]` ($2 \times 1$) $\to$ `ValueError`
   - `[[1, 2]]` ($1 \times 2$) $\to$ `ValueError`

5. **Ragged and Empty Matrices (Rejected with `ValueError`)**:
   - `[[1, 2], [3]]` $\to$ `ValueError`
   - `[]` $\to$ `ValueError: Matrix cannot be empty.`
   - `[[]]` $\to$ `ValueError: Matrix cannot contain empty rows.`

6. **Invalid Types (Rejected with `TypeError`)**:
   - `[[True, 0], [0, 1]]` $\to$ `TypeError` (booleans explicitly rejected)
   - `[["a", 1], [2, 3]]` $\to$ `TypeError`

---

## 🚀 How to Run

### 1. Via Command-Line Argument
```bash
python3 utilities/Matrix-Determinant/main.py "[[1, 2], [3, 4]]"
```
Output:
```text
✅ Determinant: -2
```

### 2. Interactive Mode
Run the script without arguments:
```bash
python3 utilities/Matrix-Determinant/main.py
```
Output:
```text
============================================================
  🔢 Matrix Determinant Calculator 🔢
  Calculate the determinant of any square matrix
============================================================
🎯 Enter square matrix (e.g. [[1,2],[3,4]]): [[5]]
✅ Determinant: 5
```

---

## 🧪 Running Tests

Run the test suite using Python's standard `unittest` discovery:

```bash
python3 -m unittest discover -s utilities/Matrix-Determinant -p "test_*.py" -v
```
