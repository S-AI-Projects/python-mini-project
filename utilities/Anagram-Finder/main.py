"""
Anagram Finder CLI & Utility
Finds words in a candidate list with identical lowercase-letter multiplicities
to a query word, excluding the query itself.
"""

from collections import Counter
import sys


def find_anagrams(query: str, candidates: list[str]) -> list[str]:
    """
    Find all words in candidates that are anagrams of query.

    Contract:
    - query: str, word to compare against.
    - candidates: list of strings to search.
    - Anagram condition: same lowercase letter multiplicities (Counter(w.lower()) == Counter(query.lower())).
    - Excludes the query itself (w.lower() != query.lower()).
    - Preserves source order of candidates.
    - Leaves caller input list intact (no mutation).
    - Raises actionable TypeError on invalid input types.
    """
    if not isinstance(query, str):
        raise TypeError(f"query must be a string, got {type(query).__name__}")
    if not isinstance(candidates, (list, tuple)):
        raise TypeError(f"candidates must be a list or tuple of strings, got {type(candidates).__name__}")

    normalized_query = query.lower()
    query_counts = Counter(normalized_query)
    results = []

    for word in candidates:
        if not isinstance(word, str):
            raise TypeError(f"all candidate items must be strings, got {type(word).__name__}")
        normalized_word = word.lower()
        if normalized_word != normalized_query and Counter(normalized_word) == query_counts:
            results.append(word)

    return results


def main() -> None:
    """Command-line interface for Anagram Finder."""
    print("=" * 45)
    print("🔤 ANAGRAM FINDER 🔤")
    print("=" * 45)

    if len(sys.argv) >= 3:
        query = sys.argv[1]
        candidates = sys.argv[2:]
    else:
        query = input("Enter query word: ").strip()
        raw_words = input("Enter candidate words (space or comma separated): ").strip()
        candidates = [w.strip() for w in raw_words.replace(",", " ").split() if w.strip()]

    print(f"\nQuery word: '{query}'")
    print(f"Candidates: {candidates}")

    matches = find_anagrams(query, candidates)
    print(f"\nFound {len(matches)} anagram(s): {matches}\n")


if __name__ == "__main__":
    main()
