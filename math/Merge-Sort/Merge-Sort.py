import sys
import os

# Add project root to sys.path
if "__file__" in globals():
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
else:
    sys.path.append(os.path.abspath(os.getcwd()))

import importlib.util

# Load validation module directly to avoid broken package __init__.py
_val_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "utils", "validation.py"))
_val_spec = importlib.util.spec_from_file_location("validation", _val_path)
_val_mod = importlib.util.module_from_spec(_val_spec)
_val_spec.loader.exec_module(_val_mod)
get_choice = _val_mod.get_choice
get_int_list = _val_mod.get_int_list


def merge_sort(arr: list[int], reverse: bool = False) -> list[int]:
    """Sorts a list of integers using the Merge Sort algorithm.

    Args:
        arr: The list of integers to sort.
        reverse: If True, sorts in descending order. Otherwise, ascending.

    Returns:
        A new sorted list.

    Example:
        For [3, 1, 2], the list splits into [3] and [1, 2]. The right partition
        is merged into [1, 2]. The final merge combines [3] with [1, 2],
        producing [1, 2, 3].

        >>> merge_sort([3, 1, 2])
        [1, 2, 3]
        >>> merge_sort([3, 1, 2], reverse=True)
        [3, 2, 1]
        >>> merge_sort([2, 2, 1])
        [1, 2, 2]
        >>> merge_sort([])
        []
    """
    # Base case: a list of 0 or 1 elements is already sorted
    if len(arr) <= 1:
        return arr.copy()

    # Divide: split the list into two halves
    mid = len(arr) // 2
    left = merge_sort(arr[:mid], reverse)
    right = merge_sort(arr[mid:], reverse)

    # Conquer: merge the two sorted halves
    return merge(left, right, reverse)


def merge(left: list[int], right: list[int], reverse: bool = False) -> list[int]:
    """Merges two sorted lists into one sorted list.

    Args:
        left: The left sorted list.
        right: The right sorted list.
        reverse: If True, merges in descending order. Otherwise, ascending.

    Returns:
        A single merged and sorted list.
    """
    result = []
    i = 0
    j = 0

    while i < len(left) and j < len(right):
        if not reverse and left[i] <= right[j]:
            result.append(left[i])
            i += 1
        elif reverse and left[i] >= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    # Append any remaining elements
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def main() -> None:
    print("=" * 50)
    print("🔀 MERGE SORT INTERACTIVE TOOL 🔀")
    print("=" * 50)
    print("Sort a list of numbers in Ascending or Descending order.\n")

    while True:
        print("=" * 50)
        arr = get_int_list(
            prompt="➡️  Enter numbers to sort separated by spaces (e.g., 64 34 25): ",
            error_empty="❌ Error: Input cannot be empty!",
            error_invalid="❌ Error: Please enter valid integers only."
        )

        print("\nChoose sorting order:")
        print("1️⃣  Ascending")
        print("2️⃣  Descending")
        order_choice = get_choice(
            prompt="🎯 Enter your choice (1 or 2): ",
            choices=["1", "2"],
            error_invalid="❌ Invalid sorting choice! Please select 1 or 2."
        )

        reverse = (order_choice == "2")
        sorted_arr = merge_sort(arr, reverse)

        print(f"\n📊 Original list: {arr}")
        if reverse:
            print(f"✅ Sorted list (Descending): {sorted_arr}")
        else:
            print(f"✅ Sorted list (Ascending): {sorted_arr}")

        again = input("\n🔄 Do you want to sort another list? (y/n): ").strip().lower()
        if again != 'y':
            print("\n👋 Thanks for using Merge Sort Tool! Goodbye!\n")
            break


if __name__ == "__main__":
    main()