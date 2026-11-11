"""
Tests for utilities/Fake-News-Headline-Generator/Fake-News-Headline-Generator.py

Validates:
- Module import safety (no CLI execution or side effects on import).
- Smallest valid fixture (empty inputs default to general mode).
- Ordinary fixture (sports mode with custom subject and target).
- Boundary inputs (invalid mode fallback, invalid loop input prompt retry).
- Case insensitivity for mode selection.
- Repeatability in fresh isolated state.
- Input isolation across successive executions.
- Immutability of global collections (modes, templates).
- Deduplication while-loop behavior.
- Membership validation for mocked choices (impossible choices rejected).
"""

import copy
import importlib.util
from pathlib import Path
import sys
from unittest.mock import patch

import pytest

MODULE_PATH = (
    Path(__file__).resolve().parent.parent
    / "utilities"
    / "Fake-News-Headline-Generator"
    / "Fake-News-Headline-Generator.py"
)


def load_module():
    """Load Fake-News-Headline-Generator module dynamically."""
    spec = importlib.util.spec_from_file_location("fake_news_gen", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["fake_news_gen"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def fake_news_mod():
    return load_module()


def make_validating_choice(expected_choices):
    """
    Return a callable for random.choice that validates that each predetermined
    choice exists in the actual candidate sequence passed by the application.
    """
    it = iter(expected_choices)

    def validating_choice(seq):
        val = next(it)
        assert val in seq, (
            f"Mocked choice {val!r} does not exist in candidate sequence {seq!r}"
        )
        return val

    return validating_choice


def test_module_import_clean(fake_news_mod):
    """Importing the module must not execute main() and must expose modes and templates."""
    assert hasattr(fake_news_mod, "main")
    assert hasattr(fake_news_mod, "modes")
    assert hasattr(fake_news_mod, "templates")
    assert "general" in fake_news_mod.modes
    assert "sports" in fake_news_mod.modes
    assert "political" in fake_news_mod.modes
    assert "chaotic" in fake_news_mod.modes
    assert len(fake_news_mod.templates) == 5


def test_smallest_valid_fixture(fake_news_mod, capsys):
    """
    Case 1: Smallest valid input
    - mode="" (defaults to general)
    - custom_subject=""
    - custom_target=""
    - user_input="no"
    Validating choices:
    - subject: "Shahrukh Khan" (modes["general"]["subjects"][0])
    - action: "launches" (in modes["general"]["actions"])
    - target: "a giant samosa" (modes["general"]["actions"]["launches"]["items"][0])
    - template: "BREAKING NEWS: {subject} {action} {target}!" (templates[0])
    """
    inputs = ["", "", "", "no"]
    choices = [
        "Shahrukh Khan",
        "launches",
        "a giant samosa",
        "BREAKING NEWS: {subject} {action} {target}!",
    ]
    val_choice = make_validating_choice(choices)

    with patch("builtins.input", side_effect=inputs), patch("random.choice", side_effect=val_choice):
        fake_news_mod.main()

    captured = capsys.readouterr().out
    assert "AVAILABLE MODES: GENERAL | SPORTS | POLITICAL | CHAOTIC" in captured
    assert "BREAKING NEWS: Shahrukh Khan launches a giant samosa!" in captured
    assert "THANKS FOR USING THE FAKE NEWS GENERATOR. HAVE A FUN DAY!" in captured


def test_ordinary_fixture(fake_news_mod, capsys):
    """
    Case 2: Ordinary input
    - mode="sports"
    - custom_subject="The Coach"
    - custom_target="10 golden bats"
    - user_input="no"
    Validating choices:
    - subject: "The Coach" (appended to subjects from custom input)
    - action: "orders" (in modes["sports"]["actions"])
    - target: "10 golden bats" (appended to targets from custom input)
    - template: "VIRAL: {subject} spotted {action} {target}!" (templates[3])
    """
    inputs = ["sports", "The Coach", "10 golden bats", "no"]
    choices = [
        "The Coach",
        "orders",
        "10 golden bats",
        "VIRAL: {subject} spotted {action} {target}!",
    ]
    val_choice = make_validating_choice(choices)

    with patch("builtins.input", side_effect=inputs), patch("random.choice", side_effect=val_choice):
        fake_news_mod.main()

    captured = capsys.readouterr().out
    assert "AVAILABLE MODES: GENERAL | SPORTS | POLITICAL | CHAOTIC" in captured
    assert "VIRAL: The Coach spotted orders 10 golden bats!" in captured
    assert "THANKS FOR USING THE FAKE NEWS GENERATOR. HAVE A FUN DAY!" in captured


def test_boundary_invalid_mode_and_retry(fake_news_mod, capsys):
    """
    Case 3: Boundary input (Invalid mode fallback and invalid retry prompt)
    - mode="invalid_mode" (falls back to general)
    - custom_subject=""
    - custom_target=""
    - user_inputs=["maybe", "no"]
    Validating choices:
    Iteration 1:
    - subject: "Virat Kohli" (modes["general"]["subjects"][1])
    - action: "eats" (in modes["general"]["actions"])
    - target: "47 pani puris" (modes["general"]["actions"]["eats"]["items"][0])
    - template: "SHOCKING: {subject} suddenly {action} {target}!" (templates[1])
    Iteration 2:
    - subject: "A Mumbai Cat" (modes["general"]["subjects"][3])
    - action: "declares war on" (in modes["general"]["actions"])
    - target: "slow internet" (modes["general"]["actions"]["declares war on"]["items"][0])
    - template: "JUST IN: {subject} officially {action} {target}!" (templates[4])
    """
    inputs = ["invalid_mode", "", "", "maybe", "no"]
    choices = [
        "Virat Kohli",
        "eats",
        "47 pani puris",
        "SHOCKING: {subject} suddenly {action} {target}!",
        "A Mumbai Cat",
        "declares war on",
        "slow internet",
        "JUST IN: {subject} officially {action} {target}!",
    ]
    val_choice = make_validating_choice(choices)

    with patch("builtins.input", side_effect=inputs), patch("random.choice", side_effect=val_choice):
        fake_news_mod.main()

    captured = capsys.readouterr().out
    assert "SHOCKING: Virat Kohli suddenly eats 47 pani puris!" in captured
    assert "INVALID INPUT. GENERATING ANOTHER HEADLINE..." in captured
    assert "JUST IN: A Mumbai Cat officially declares war on slow internet!" in captured
    assert "THANKS FOR USING THE FAKE NEWS GENERATOR. HAVE A FUN DAY!" in captured


def test_mode_case_insensitivity(fake_news_mod, capsys):
    """
    Case 4: Mode case-insensitivity
    - mode="POLITICAL" (normalized to "political")
    - custom_subject=""
    - custom_target=""
    - user_input="no"
    Validating choices:
    - subject: "Prime Minister Modi" (modes["political"]["subjects"][0])
    - action: "launches" (in modes["political"]["actions"])
    - target: "a new tax policy" (modes["political"]["actions"]["launches"]["items"][0])
    - template: "EXCLUSIVE: {subject} reportedly {action} {target}!" (templates[2])
    """
    inputs = ["POLITICAL", "", "", "no"]
    choices = [
        "Prime Minister Modi",
        "launches",
        "a new tax policy",
        "EXCLUSIVE: {subject} reportedly {action} {target}!",
    ]
    val_choice = make_validating_choice(choices)

    with patch("builtins.input", side_effect=inputs), patch("random.choice", side_effect=val_choice):
        fake_news_mod.main()

    captured = capsys.readouterr().out
    assert "AVAILABLE MODES: GENERAL | SPORTS | POLITICAL | CHAOTIC" in captured
    assert "EXCLUSIVE: Prime Minister Modi reportedly launches a new tax policy!" in captured
    assert "THANKS FOR USING THE FAKE NEWS GENERATOR. HAVE A FUN DAY!" in captured


def test_repeatability_in_isolated_state(fake_news_mod, capsys):
    """Running the same fixture twice in isolated state produces identical output."""
    inputs = ["", "", "", "no"]
    choices = [
        "Shahrukh Khan",
        "launches",
        "a giant samosa",
        "BREAKING NEWS: {subject} {action} {target}!",
    ]

    # Run A
    val_choice_a = make_validating_choice(choices)
    with patch("builtins.input", side_effect=list(inputs)), patch("random.choice", side_effect=val_choice_a):
        fake_news_mod.main()
    out_a = capsys.readouterr().out

    # Run B
    val_choice_b = make_validating_choice(choices)
    with patch("builtins.input", side_effect=list(inputs)), patch("random.choice", side_effect=val_choice_b):
        fake_news_mod.main()
    out_b = capsys.readouterr().out

    assert out_a == out_b
    assert "BREAKING NEWS: Shahrukh Khan launches a giant samosa!" in out_a


def test_input_isolation_between_calls(fake_news_mod, capsys):
    """
    Run fixture 1, then run fixture 2 with custom additions, then run fixture 1 again.
    Fixture 1's results must be unaffected by the intervening run.
    """
    fixture1_inputs = ["", "", "", "no"]
    fixture1_choices = [
        "Shahrukh Khan",
        "launches",
        "a giant samosa",
        "BREAKING NEWS: {subject} {action} {target}!",
    ]

    fixture2_inputs = ["sports", "The Coach", "10 golden bats", "no"]
    fixture2_choices = [
        "The Coach",
        "orders",
        "10 golden bats",
        "VIRAL: {subject} spotted {action} {target}!",
    ]

    # Run 1: Fixture 1
    val_1 = make_validating_choice(fixture1_choices)
    with patch("builtins.input", side_effect=list(fixture1_inputs)), patch("random.choice", side_effect=val_1):
        fake_news_mod.main()
    out_1 = capsys.readouterr().out

    # Run 2: Fixture 2 (intervening call with custom subject and target)
    val_2 = make_validating_choice(fixture2_choices)
    with patch("builtins.input", side_effect=list(fixture2_inputs)), patch("random.choice", side_effect=val_2):
        fake_news_mod.main()
    out_2 = capsys.readouterr().out
    assert "The Coach" in out_2

    # Run 3: Fixture 1 repeated
    val_3 = make_validating_choice(fixture1_choices)
    with patch("builtins.input", side_effect=list(fixture1_inputs)), patch("random.choice", side_effect=val_3):
        fake_news_mod.main()
    out_3 = capsys.readouterr().out

    assert out_1 == out_3
    assert "The Coach" not in out_3
    assert "10 golden bats" not in out_3


def test_global_immutability(fake_news_mod, capsys):
    """Custom subjects or targets must not mutate the global modes or templates."""
    modes_before = copy.deepcopy(fake_news_mod.modes)
    templates_before = copy.deepcopy(fake_news_mod.templates)

    inputs = ["general", "Custom Subject X", "Custom Target Y", "no"]
    choices = [
        "Custom Subject X",
        "launches",
        "Custom Target Y",
        "BREAKING NEWS: {subject} {action} {target}!",
    ]
    val_choice = make_validating_choice(choices)

    with patch("builtins.input", side_effect=inputs), patch("random.choice", side_effect=val_choice):
        fake_news_mod.main()

    capsys.readouterr()  # discard output

    assert fake_news_mod.modes == modes_before
    assert fake_news_mod.templates == templates_before


def test_deduplication_inner_loop(fake_news_mod, capsys):
    """
    Test deduplication loop: if the first formatted headline equals last_headline,
    the inner while loop calls random.choice(templates) again until it differs.
    """
    inputs = ["general", "", "", "yes", "no"]
    # Iteration 1 generates: "BREAKING NEWS: Shahrukh Khan launches a giant samosa!"
    # Iteration 2 chooses same subject, action, target, and first template is identical,
    # so line 240 is entered and chooses templates[1].
    choices = [
        # Iteration 1:
        "Shahrukh Khan",
        "launches",
        "a giant samosa",
        "BREAKING NEWS: {subject} {action} {target}!",
        # Iteration 2:
        "Shahrukh Khan",
        "launches",
        "a giant samosa",
        "BREAKING NEWS: {subject} {action} {target}!",  # matches last_headline
        "SHOCKING: {subject} suddenly {action} {target}!",  # resampled template
    ]
    val_choice = make_validating_choice(choices)

    with patch("builtins.input", side_effect=inputs), patch("random.choice", side_effect=val_choice):
        fake_news_mod.main()

    captured = capsys.readouterr().out
    assert "BREAKING NEWS: Shahrukh Khan launches a giant samosa!" in captured
    assert "SHOCKING: Shahrukh Khan suddenly launches a giant samosa!" in captured


def test_validating_choice_rejects_impossible_choice():
    """Ensure make_validating_choice catches impossible choices rather than blindly accepting them."""
    val_choice = make_validating_choice(["Impossible Alien"])
    with pytest.raises(AssertionError, match="does not exist in candidate sequence"):
        val_choice(["Virat Kohli", "Rohit Sharma"])
