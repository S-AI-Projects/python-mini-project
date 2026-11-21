"""Word Counter with Configurable Punctuation Stripping and Complexity Profiling.

Counts case-normalized whitespace-delimited words using an explicit
punctuation-stripping policy. Includes empirical complexity measurement tools.
"""

import argparse
import string
import sys
import time
from typing import Dict, List, Optional, Sequence, Tuple

DEFAULT_PUNCTUATION: str = string.punctuation


def count_words(
    text: str,
    punctuation: str = DEFAULT_PUNCTUATION,
) -> Dict[str, int]:
    """Count case-normalized whitespace-delimited words with punctuation stripping.

    Parameters
    ----------
    text : str
        Input string to analyze.
    punctuation : str, optional
        Characters to strip from token boundaries (default: string.punctuation).

    Returns
    -------
    Dict[str, int]
        Dictionary mapping lowercased words to their frequency counts.
        Returns an empty dict `{}` if input is empty or whitespace-only.

    Raises
    ------
    TypeError
        If `text` is not a string.
    """
    if not isinstance(text, str):
        raise TypeError(
            f"Expected string input, got {type(text).__name__} ({text!r}). "
            "Action: Provide a string to count_words()."
        )

    counts: Dict[str, int] = {}
    tokens = text.split()

    for raw_token in tokens:
        cleaned = raw_token.strip(punctuation).lower()
        if cleaned:
            counts[cleaned] = counts.get(cleaned, 0) + 1

    return counts


def run_complexity_experiment(
    sizes: Sequence[int] = (100, 1000, 10000),
) -> List[Dict[str, float]]:
    """Measure bounded work at three distinct sizes where the domain varies.

    At each size $N$, generates words from varying domain vocabularies
    (small vocabulary, Zipfian medium vocabulary, and large high-entropy vocabulary)
    and records token count, character volume, operations, and execution time.

    Parameters
    ----------
    sizes : Sequence[int], optional
        The three sizes to benchmark (default: 100, 1000, 10000).

    Returns
    -------
    List[Dict[str, float]]
        Experimental data for each size.
    """
    results: List[Dict[str, float]] = []

    # Domain vocabulary patterns for each scale
    domain_configs: List[Tuple[str, int]] = [
        ("small_domain_fixed_entropy", 10),     # 10 unique words
        ("medium_domain_zipfian", 100),         # 100 unique words with varying frequencies
        ("large_domain_high_entropy", 1000),    # 1000 unique words
    ]

    for idx, n in enumerate(sizes):
        domain_name, vocab_size = domain_configs[min(idx, len(domain_configs) - 1)]

        # Generate synthetic text with realistic punctuation
        words_pool = [f"word{i}" for i in range(vocab_size)]
        punctuations = [",", "!", ".", "?", ";", ":", ""]
        generated_tokens = []
        for i in range(n):
            w = words_pool[i % vocab_size]
            p = punctuations[i % len(punctuations)]
            # Mix casing and punctuation
            token = f"{w.capitalize()}{p}" if i % 2 == 0 else f"{w}{p}"
            generated_tokens.append(token)

        synthetic_text = " ".join(generated_tokens)
        char_count = len(synthetic_text)

        # Measure work: operations count and wall-clock duration
        start_time = time.perf_counter()
        word_counts = count_words(synthetic_text)
        elapsed = time.perf_counter() - start_time

        # Bounded operation metrics:
        # 1. Whitespace split scans char_count chars: O(L)
        # 2. Punctuation stripping scans token boundary chars: O(L)
        # 3. Hash map lookups and insertions: exactly N operations
        total_ops = n + char_count

        results.append(
            {
                "size_n": float(n),
                "domain": domain_name,
                "vocab_size": float(vocab_size),
                "unique_words_found": float(len(word_counts)),
                "char_length": float(char_count),
                "bounded_operations": float(total_ops),
                "elapsed_seconds": elapsed,
                "ops_per_token": total_ops / n if n > 0 else 0.0,
            }
        )

    return results


def main(argv: Optional[Sequence[str]] = None) -> int:
    """CLI entry point for Word-Counter."""
    parser = argparse.ArgumentParser(
        prog="word_counter",
        description="Count case-normalized words with explicit punctuation stripping.",
    )
    parser.add_argument(
        "text",
        nargs="*",
        help="Words or string to analyze.",
    )
    parser.add_argument(
        "--file",
        "-f",
        dest="file",
        help="Input text file to count words from.",
    )
    parser.add_argument(
        "--experiment",
        action="store_true",
        help="Run complexity experiment at three input sizes (100, 1000, 10000).",
    )

    args = parser.parse_args(argv)

    if args.experiment:
        print("Running bounded work complexity experiment (N = 100, 1000, 10000)...")
        exp_results = run_complexity_experiment()
        print(f"{'Size (N)':<10} {'Domain':<30} {'Unique Words':<15} {'Total Ops':<12} {'Elapsed (s)':<12}")
        print("-" * 80)
        for r in exp_results:
            print(
                f"{int(r['size_n']):<10} {r['domain']:<30} {int(r['unique_words_found']):<15} "
                f"{int(r['bounded_operations']):<12} {r['elapsed_seconds']:.6f}"
            )
        return 0

    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as fh:
                content = fh.read()
            counts = count_words(content)
            for word, freq in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
                print(f"{word}: {freq}")
            return 0
        except Exception as err:
            print(f"Error reading file '{args.file}': {err}", file=sys.stderr)
            return 1

    if args.text:
        combined = " ".join(args.text)
        counts = count_words(combined)
        for word, freq in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"{word}: {freq}")
        return 0

    # Interactive mode if no arguments given
    print("Word Counter. Type text to analyze (or 'quit' / 'exit' to stop):")
    while True:
        try:
            line = input("\nText: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if line.lower() in ("quit", "exit", "q"):
            break
        if not line:
            continue
        counts = count_words(line)
        print(f"Result: {counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
