import importlib.util
import json
import os
import random
import string
from pathlib import Path

import pytest


MODULE_PATH = (
    Path(__file__).resolve().parent.parent
    / "games"
    / "Hangman-Game"
    / "Hangman-Game.py"
)


def record_case(name, inputs, expected, actual):
    evidence_file = os.environ.get("HANGMAN_CHECK_EVIDENCE_FILE")
    if evidence_file is None:
        return

    with Path(evidence_file).open("a", encoding="utf-8") as file:
        file.write(
            json.dumps(
                {
                    "check": name,
                    "inputs": inputs,
                    "expected": expected,
                    "actual": actual,
                }
            )
            + "\n"
        )


@pytest.fixture
def hangman():
    spec = importlib.util.spec_from_file_location("hangman_game", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_game(hangman, monkeypatch, word, inputs):
    remaining_inputs = iter(inputs)
    monkeypatch.setattr(
        hangman.random,
        "choice",
        lambda choices: next(item for item in choices if item["word"] == word),
    )
    monkeypatch.setattr(
        "builtins.input", lambda _prompt="": next(remaining_inputs)
    )
    monkeypatch.setattr(
        hangman, "print_victory_banner", lambda: print("VICTORY")
    )
    monkeypatch.setattr(
        hangman, "print_game_over_banner", lambda: print("GAME OVER")
    )
    return hangman.main()


def test_main_tracks_smallest_valid_guess_once(hangman, monkeypatch, capsys):
    # Preconditions: "java" is in main's word_data (source line 94), it is
    # selected and assigned to word (lines 146-149), and both guess lists
    # start empty (lines 151-152). A valid guess is one alphabetic character
    # (line 184); correct guesses are appended after that validation (lines
    # 194-198).
    literal_inputs = ["j", "a", "v", "no"]
    expected_guessed_letters = ["j", "a", "v"]
    expected_correct_letters = ["j", "a", "v"]
    expected_output = [
        "Word: _ _ _ _ ",
        "✓ Correct! 'j' is in the word.",
        "✓ Correct! 'a' is in the word.",
        "✓ Correct! 'v' is in the word.",
        "VICTORY",
        "The word was: java",
        "You guessed it with 6 attempts remaining!",
    ]

    result = run_game(hangman, monkeypatch, "java", literal_inputs)
    output = capsys.readouterr().out
    record_case(
        "test_main_tracks_smallest_valid_guess_once",
        literal_inputs,
        {
            "return": None,
            "guessed_letters": expected_guessed_letters,
            "correct_letters": expected_correct_letters,
            "output_contains": expected_output,
        },
        {
            "return": result,
            "guessed_letters": hangman.guessed_letters,
            "correct_letters": hangman.correct_letters,
            "output_contains": [
                line for line in expected_output if line in output
            ],
        },
    )

    assert result is None
    assert hangman.guessed_letters == expected_guessed_letters
    assert hangman.correct_letters == expected_correct_letters
    for line in expected_output:
        assert line in output


def test_main_records_only_unique_correct_letters_for_ordinary_game(
    hangman, monkeypatch, capsys
):
    # Preconditions: "python" is in main's word_data (source line 93), it is
    # selected and assigned to word (lines 146-149), and both guess lists
    # start empty (lines 151-152). Validation rejects non-single-letter input
    # (line 184), duplicate guesses are skipped (lines 189-192), and each new
    # valid guess is recorded before checking whether it is correct (lines
    # 194-201).
    literal_inputs = ["x", "p", "p", "!", "y", "t", "h", "o", "n", "no"]
    expected_guessed_letters = ["x", "p", "y", "t", "h", "o", "n"]
    expected_correct_letters = ["p", "y", "t", "h", "o", "n"]
    expected_output = [
        "✗ Wrong! 'x' is not in the word.",
        "You already guessed that letter!",
        "Please enter a single letter!",
        "✓ Correct! 'p' is in the word.",
        "✓ Correct! 'y' is in the word.",
        "✓ Correct! 't' is in the word.",
        "✓ Correct! 'h' is in the word.",
        "✓ Correct! 'o' is in the word.",
        "✓ Correct! 'n' is in the word.",
        "VICTORY",
        "The word was: python",
        "You guessed it with 5 attempts remaining!",
    ]

    result = run_game(hangman, monkeypatch, "python", literal_inputs)
    output = capsys.readouterr().out
    record_case(
        "test_main_records_only_unique_correct_letters_for_ordinary_game",
        literal_inputs,
        {
            "return": None,
            "guessed_letters": expected_guessed_letters,
            "correct_letters": expected_correct_letters,
            "output_contains": expected_output,
        },
        {
            "return": result,
            "guessed_letters": hangman.guessed_letters,
            "correct_letters": hangman.correct_letters,
            "output_contains": [
                line for line in expected_output if line in output
            ],
        },
    )

    assert result is None
    assert hangman.guessed_letters == expected_guessed_letters
    assert hangman.correct_letters == expected_correct_letters
    for line in expected_output:
        assert line in output


def test_main_tracks_guesses_for_100_seeded_valid_cases(
    hangman, monkeypatch, capsys
):
    # Preconditions: "java" and "python" are in main's word_data (source
    # lines 93-94), each is selected and assigned to word (lines 146-149),
    # and both lists start empty (lines 151-152). Lowercase ASCII letters
    # satisfy the source's one-letter alphabetic validation (line 184);
    # new valid guesses are appended once and classified (lines 194-201).
    rng = random.Random(20261117)
    words = ["java", "python"]
    cases = []
    while len(cases) < 100:
        word = rng.choice(words)
        guesses = rng.sample(string.ascii_lowercase, rng.randint(1, 5))
        if set(word).issubset(guesses):
            continue

        misses_so_far = sum(letter not in word for letter in guesses)
        wrong_letters = [
            letter
            for letter in string.ascii_lowercase
            if letter not in word and letter not in guesses
        ]
        misses_to_finish = 6 - misses_so_far
        all_guesses = guesses + wrong_letters[:misses_to_finish]
        cases.append((word, guesses, all_guesses))

    assert len(cases) == 100
    for word, generated_guesses, all_guesses in cases:
        assert all(len(letter) == 1 and letter.isalpha() for letter in all_guesses)
        assert all(letter.isascii() for letter in all_guesses)
        assert len(set(all_guesses)) == len(all_guesses)
        assert set(word) - set(generated_guesses)

        literal_inputs = all_guesses + ["no"]
        expected_guessed_letters = all_guesses
        expected_correct_letters = [
            letter for letter in all_guesses if letter in word
        ]

        result = run_game(hangman, monkeypatch, word, literal_inputs)
        output = capsys.readouterr().out
        expected_output = ["GAME OVER", f"The word was: {word}"]
        record_case(
            "test_main_tracks_guesses_for_100_seeded_valid_cases",
            literal_inputs,
            {
                "word": word,
                "return": None,
                "guessed_letters": expected_guessed_letters,
                "correct_letters": expected_correct_letters,
                "output_contains": expected_output,
            },
            {
                "word": hangman.word,
                "return": result,
                "guessed_letters": hangman.guessed_letters,
                "correct_letters": hangman.correct_letters,
                "output_contains": [
                    line for line in expected_output if line in output
                ],
            },
        )

        assert result is None
        assert hangman.guessed_letters == expected_guessed_letters
        assert hangman.correct_letters == expected_correct_letters
        assert "GAME OVER" in output
        assert f"The word was: {word}" in output
