"""
Matrix Determinant Calculator

Provides core functions to validate and compute the determinant of square
matrices, as well as an interactive and argument-based CLI interface.
"""

from __future__ import annotations

import ast
from fractions import Fraction
import json
import sys
from typing import Union


Number = Union[int, float]
Matrix = list[list[Number]]


def validate_square_matrix(matrix: Matrix) -> int:
    """Validate that the input is a non-empty square matrix containing numbers.

    Returns the dimension n of the n x n matrix.
    Raises ValueError for empty, ragged, or nonsquare matrices.
    Raises TypeError for non-numeric or boolean elements, or non-list containers.
    """
    if not isinstance(matrix, list):
        raise TypeError("Matrix must be a list of lists.")
    if len(matrix) == 0:
        raise ValueError("Matrix cannot be empty.")

    n = len(matrix)
    for row in matrix:
        if not isinstance(row, list):
            raise TypeError("Each matrix row must be a list.")
        if len(row) == 0:
            raise ValueError("Matrix cannot contain empty rows.")
        if len(row) != n:
            raise ValueError(
                f"Matrix must be square: expected {n} columns, but found row with {len(row)} columns."
            )
        for element in row:
            if isinstance(element, bool):
                raise TypeError(
                    f"Invalid element {element!r}: boolean values are not permitted in matrices."
                )
            if not isinstance(element, (int, float)):
                raise TypeError(
                    f"Invalid element {element!r}: elements must be int or float, got {type(element).__name__}."
                )

    return n


def calculate_determinant(matrix: Matrix) -> Number:
    """Calculate the determinant of a square matrix.

    Returns an int for matrices consisting entirely of integers, and a float
    otherwise.
    """
    n = validate_square_matrix(matrix)

    if n == 1:
        return matrix[0][0]

    if n == 2:
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]

    all_integers = all(isinstance(element, int) for row in matrix for element in row)

    if all_integers:
        mat: list[list[Fraction]] = [
            [Fraction(element) for element in row] for row in matrix
        ]
        sign = 1
        for i in range(n):
            pivot = i
            while pivot < n and mat[pivot][i] == 0:
                pivot += 1
            if pivot == n:
                return 0

            if pivot != i:
                mat[i], mat[pivot] = mat[pivot], mat[i]
                sign = -sign

            pivot_val = mat[i][i]
            for j in range(i + 1, n):
                if mat[j][i] != 0:
                    factor = mat[j][i] / pivot_val
                    for k in range(i, n):
                        mat[j][k] -= factor * mat[i][k]

        det_frac = Fraction(sign)
        for i in range(n):
            det_frac *= mat[i][i]

        return int(det_frac)

    # Float path with partial pivoting
    float_mat: list[list[float]] = [
        [float(element) for element in row] for row in matrix
    ]
    sign = 1
    for i in range(n):
        max_row = i
        max_val = abs(float_mat[i][i])
        for r in range(i + 1, n):
            if abs(float_mat[r][i]) > max_val:
                max_val = abs(float_mat[r][i])
                max_row = r

        if max_val < 1e-15:
            return 0.0

        if max_row != i:
            float_mat[i], float_mat[max_row] = float_mat[max_row], float_mat[i]
            sign = -sign

        pivot_val = float_mat[i][i]
        for j in range(i + 1, n):
            if abs(float_mat[j][i]) > 1e-15:
                factor = float_mat[j][i] / pivot_val
                for k in range(i, n):
                    float_mat[j][k] -= factor * float_mat[i][k]

    det_float = float(sign)
    for i in range(n):
        det_float *= float_mat[i][i]

    return det_float


determinant = calculate_determinant


def parse_matrix(text: str) -> Matrix:
    """Parse a matrix literal string safely.

    Never uses eval. Uses ast.literal_eval or json.loads.
    """
    cleaned = text.strip()
    if not cleaned:
        raise ValueError("Input text is empty.")

    try:
        data = ast.literal_eval(cleaned)
    except (ValueError, SyntaxError) as exc:
        try:
            data = json.loads(cleaned)
        except Exception:
            raise ValueError(f"Could not parse matrix input: {exc}") from exc

    if not isinstance(data, list):
        raise ValueError("Parsed data is not a matrix list.")

    return data


def main() -> None:
    """CLI Entry point for Matrix Determinant calculator."""
    if len(sys.argv) > 1:
        raw_input = sys.argv[1].strip()
    else:
        print("=" * 60)
        print("  🔢 Matrix Determinant Calculator 🔢")
        print("  Calculate the determinant of any square matrix")
        print("=" * 60)
        try:
            raw_input = input("🎯 Enter square matrix (e.g. [[1,2],[3,4]]): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Operation cancelled.")
            sys.exit(0)

    if not raw_input:
        print("❌ Error: Matrix input cannot be empty.")
        sys.exit(1)

    try:
        matrix = parse_matrix(raw_input)
        result = calculate_determinant(matrix)
        print(f"✅ Determinant: {result}")
    except (ValueError, TypeError) as err:
        print(f"❌ Error: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
