"""
Palindrome Finder CLI & Utility
Identifies words that read the same forwards and backwards after lowercase normalization,
preserving source order and handling empty words by explicit policy.
"""

import sys


def is_palindrome(word: str) -> bool:
    """
    Check if a single word is a palindrome after lowercase normalization.

    Stated Policy:
    - Empty words ("") are excluded as non-palindromes (length must be > 0).
    - Decisive condition: normalized == normalized[::-1] and len(normalized) > 0.
    """
    if not isinstance(word, str):
        raise TypeError(f"word must be a string, got {type(word).__name__}")

    normalized = word.lower()
    # Decisive condition:
    return len(normalized) > 0 and normalized == normalized[::-1]


def find_palindromes(words: list[str]) -> list[str]:
    """
    Return words that equal their reversal after lowercase normalization,
    preserving source order.

    Contract:
    - words: list or tuple of strings.
    - Example: ['Level', 'cat', 'radar'] -> ['Level', 'radar']
    - Original word casing is preserved in the output.
    - Empty strings ('') are excluded according to stated policy.
    - Leaves caller input list intact (no mutation).
    """
    if not isinstance(words, (list, tuple)):
        raise TypeError(f"words must be a list or tuple of strings, got {type(words).__name__}")

    for w in words:
        if not isinstance(w, str):
            raise TypeError(f"all items in words must be strings, got {type(w).__name__}")

    return [w for w in words if is_palindrome(w)]


def main() -> None:
    """Command-line interface for Palindrome Finder."""
    print("=" * 45)
    print("🔁 PALINDROME FINDER 🔁")
    print("=" * 45)

    if len(sys.argv) > 1:
        words = sys.argv[1:]
    else:
        raw = input("Enter words separated by spaces or commas: ").strip()
        words = [w.strip() for w in raw.replace(",", " ").split() if w.strip()]

    print(f"\nInput words: {words}")
    palindromes = find_palindromes(words)
    print(f"Palindromes found ({len(palindromes)}): {palindromes}\n")


if __name__ == "__main__":
    main()
