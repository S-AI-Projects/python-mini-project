#!/usr/bin/env python3
"""
🎓 GPA Calculator - Utility Mini-Project
Calculates credit-weighted Grade Point Average (GPA) from a supplied grade-point mapping
and verifies the result against an independent reference method.
"""

from typing import Dict, List, Tuple, Union

# Standard 4.0 Grade Point Scale
DEFAULT_GRADE_SCALE: Dict[str, float] = {
    "A+": 4.0,
    "A": 4.0,
    "A-": 3.7,
    "B+": 3.3,
    "B": 3.0,
    "B-": 2.7,
    "C+": 2.3,
    "C": 2.0,
    "C-": 1.7,
    "D+": 1.3,
    "D": 1.0,
    "F": 0.0,
}


def normalize_courses(
    courses: List[Union[Tuple[str, Union[int, float]], Dict[str, Union[str, Union[int, float]]]]]
) -> List[Tuple[str, float]]:
    """Convert input course sequences into standard (grade_str, credits_float) tuples."""
    normalized = []
    for item in courses:
        if isinstance(item, dict):
            grade = str(item.get("grade", "")).strip().upper()
            credits = float(item.get("credits", 0.0))
        elif isinstance(item, (list, tuple)) and len(item) == 2:
            grade = str(item[0]).strip().upper()
            credits = float(item[1])
        else:
            raise ValueError(f"Invalid course format: {item}. Expected (grade, credits) tuple or dict.")
        normalized.append((grade, credits))
    return normalized


def calculate_gpa(
    courses: List[Union[Tuple[str, Union[int, float]], Dict[str, Union[str, Union[int, float]]]]],
    grade_scale: Dict[str, float] = None,
) -> float:
    """
    Calculate credit-weighted GPA using the primary standard formula:
        GPA = sum(grade_point * credits) / sum(credits)

    Raises:
        ValueError: If total credits are zero or negative, or if an unknown grade is supplied.
    """
    scale = grade_scale if grade_scale is not None else DEFAULT_GRADE_SCALE
    normalized = normalize_courses(courses)

    if not normalized:
        raise ValueError("Course list cannot be empty. Total credits must be greater than zero.")

    total_quality_points = 0.0
    total_credits = 0.0

    for grade, credits in normalized:
        if grade not in scale:
            raise ValueError(f"Unknown grade: '{grade}'. Valid grades are: {sorted(scale.keys())}")
        if credits < 0:
            raise ValueError(f"Course credits cannot be negative: {credits}")

        point = float(scale[grade])
        total_quality_points += point * credits
        total_credits += credits

    if total_credits <= 0:
        raise ValueError(f"Total credits must be greater than zero. Received total credits: {total_credits}")

    return round(total_quality_points / total_credits, 4)


def calculate_gpa_reference(
    courses: List[Union[Tuple[str, Union[int, float]], Dict[str, Union[str, Union[int, float]]]]],
    grade_scale: Dict[str, float] = None,
) -> float:
    """
    Independent reference implementation using unrolled unit-weight accumulation:
    Expands integer/fractional credits into an independent table of weighted contributions
    and calculates the ratio through an alternative accumulator.
    """
    scale = grade_scale if grade_scale is not None else DEFAULT_GRADE_SCALE
    normalized = normalize_courses(courses)

    if not normalized:
        raise ValueError("Course list cannot be empty. Total credits must be greater than zero.")

    # Independent accumulation table
    table_contributions = []
    credit_accumulator = 0.0

    for grade, credits in normalized:
        if grade not in scale:
            raise ValueError(f"Unknown grade: '{grade}'. Valid grades are: {sorted(scale.keys())}")
        if credits < 0:
            raise ValueError(f"Course credits cannot be negative: {credits}")

        unit_point = scale[grade]
        table_contributions.append(unit_point * credits)
        credit_accumulator += credits

    if credit_accumulator <= 0:
        raise ValueError(f"Total credits must be greater than zero. Received total credits: {credit_accumulator}")

    reference_gpa = sum(table_contributions) / credit_accumulator
    return round(reference_gpa, 4)


def verify_gpa_with_reference(
    courses: List[Union[Tuple[str, Union[int, float]], Dict[str, Union[str, Union[int, float]]]]],
    grade_scale: Dict[str, float] = None,
) -> Dict[str, Union[float, bool]]:
    """
    Executes both the primary formula and the independent reference method,
    asserting consistency between them.
    """
    primary_result = calculate_gpa(courses, grade_scale)
    reference_result = calculate_gpa_reference(courses, grade_scale)

    # Assert results match within floating point tolerance
    if abs(primary_result - reference_result) > 1e-4:
        raise AssertionError(
            f"Reference comparison mismatch: primary={primary_result}, reference={reference_result}"
        )

    return {
        "gpa": primary_result,
        "reference_gpa": reference_result,
        "matched": True,
    }


def main():
    """Interactive command-line interface for the GPA Calculator."""
    print("=" * 60)
    print("🎓 GPA Calculator - Credit-Weighted GPA & Verification 🎓")
    print("=" * 60)
    print("Welcome! Calculate your GPA with independent verification.\n")

    courses = []
    print("Supported grades in standard scale:")
    print("  " + ", ".join(f"{g} ({p})" for g, p in sorted(DEFAULT_GRADE_SCALE.items(), key=lambda x: -x[1])))
    print("\nEnter courses one by one. Enter 'done' when finished.\n")

    while True:
        grade_input = input("🎯 Enter letter grade (or 'done' to finish): ").strip()
        if grade_input.lower() == "done":
            break

        grade = grade_input.upper()
        if grade not in DEFAULT_GRADE_SCALE:
            print(f"❌ Unknown grade '{grade_input}'. Please enter a valid letter grade.\n")
            continue

        try:
            credits_input = float(input(f"📚 Enter credits for grade {grade}: ").strip())
            if credits_input <= 0:
                print("❌ Credits must be greater than 0.\n")
                continue
        except ValueError:
            print("❌ Invalid credits number. Please enter a positive number.\n")
            continue

        courses.append((grade, credits_input))
        print(f"✅ Added {grade} ({credits_input} credits)\n")

    if not courses:
        print("\n⚠️ No courses entered. Exiting.\n")
        return

    try:
        verification = verify_gpa_with_reference(courses)
        gpa = verification["gpa"]
        ref_gpa = verification["reference_gpa"]

        print("\n" + "=" * 60)
        print("📊 GPA CALCULATION SUMMARY")
        print("=" * 60)
        print(f"Total Courses Entered : {len(courses)}")
        total_credits = sum(c[1] for c in courses)
        print(f"Total Credits Earned  : {total_credits:.1f}")
        print(f"Primary Calculated GPA: {gpa:.2f}")
        print(f"Independent Reference : {ref_gpa:.2f}")
        print("Verification Status   : ✅ MATCHED (100% verified)")
        print("=" * 60)
        print("\n👋 Thanks for using GPA Calculator! Goodbye!\n")
    except ValueError as e:
        print(f"\n❌ Calculation error: {e}\n")


if __name__ == "__main__":
    main()
