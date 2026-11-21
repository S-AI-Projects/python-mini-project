import os
import random
import sys

# Standardized path resolution to point to project root securely
if "__file__" in globals():
    project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
else:
    project_root = os.path.abspath(os.getcwd())

if project_root not in sys.path:
    sys.path.append(project_root)

from utils.validation import get_choice, get_int

# Game constants
MIN_NUMBER = 1
MAX_NUMBER = 100

# Difficulty configuration
DIFFICULTY_ATTEMPTS = {
    "1": 15,
    "2": 10,
    "3": 5,
}

# Proximity hint thresholds
VERY_CLOSE_THRESHOLD = 3
CLOSE_THRESHOLD = 10
NOT_CLOSE_THRESHOLD = 20


def main() -> None:
    """Run the CLI Number Guessing Game.

    Domain and Boundary Contract:
    - Inputs:
        - Interactive CLI input via stdin (wrapped by utils.validation).
        - Difficulty choice:
            - Valid domain: "1" (Easy: 15 attempts), "2" (Medium: 10 attempts),
              "3" (Hard: 5 attempts, smallest attempt budget).
            - Default fallback: "" resolves to "2" (Medium).
            - Source fixture anchor: DIFFICULTY_ATTEMPTS (lines 21-25).
        - Guess number (guess_num):
            - Valid domain: [MIN_NUMBER, MAX_NUMBER] = [1, 100].
            - Boundary check: 1 <= guess_num <= 100 (line 69).
            - Out-of-bounds (0 or <=0, 101 or >=101): rejected with warning,
              does not penalize attempts or modify guess_history.
            - Smallest valid guess: 1 (MIN_NUMBER).
        - Play again choice:
            - Valid exit: 'n', 'no' (terminates game loop).
            - Valid retry: 'y', 'yes' (initiates new round).
    - Result:
        - Returns None.
    - Observable Mutation:
        - Tracks round guesses in local guess_history = [] (line 53).
        - Appends accepted in-bounds guesses sequentially (line 74).
        - Does not mutate any external caller state.
    """
    print("🎯 Welcome to the Number Guessing Game!\n")

    while True:
        print("Choose difficulty:")
        print("  1) Easy   - 15 attempts 🟢")
        print("  2) Medium - 10 attempts 🟡")
        print("  3) Hard   - 5 attempts  🔴")

        choice = get_choice(
            prompt="Select 1, 2 or 3 (default 2): ",
            choices=["1", "2", "3"],
            default="2",
            error_invalid="⚠️ Invalid selection. Please enter 1, 2 or 3."
        )

        max_attempts = DIFFICULTY_ATTEMPTS[choice]

        number = random.randint(MIN_NUMBER, MAX_NUMBER)
        attempts = 0
        guess_history = []
        won = False

        print(f"\n🤔 I'm thinking of a number between {MIN_NUMBER} and {MAX_NUMBER}.")
        print(f"You have {max_attempts} attempts.")

        while attempts < max_attempts:
            remaining = max_attempts - attempts
            
            guess_num = get_int(
                prompt=f"\n👉 Guess ({remaining} left): ",
                error_empty="⚠️ Input cannot be empty.",
                error_invalid="⚠️ Invalid input. Please enter a whole number."
            )
            
            # Constraint check before incrementing attempts to avoid penalties
            if not (MIN_NUMBER <= guess_num <= MAX_NUMBER):
                print(f"⚠️ Enter a number between {MIN_NUMBER} and {MAX_NUMBER}.")
                continue

            attempts += 1
            guess_history.append(guess_num)

            if guess_num == number:
                print("\n🎉 Correct! You guessed the number.")
                print(f"✅ Number: {number}")
                print(f"🎯 Attempts: {attempts}/{max_attempts}")
                print("📜 Guesses:", ", ".join(map(str, guess_history)))
                won = True
                break

            if guess_num > number:
                print("📉 Too high.")
            else:
                print("📈 Too low.")

            # Show proximity hint
            diff = abs(guess_num - number)
            if diff <= VERY_CLOSE_THRESHOLD:
                print("🔥 Very close!")
            elif diff <= CLOSE_THRESHOLD:
                print("😊 Close.")
            elif diff <= NOT_CLOSE_THRESHOLD:
                print("😐 Not very close.")
            else:
                print("❄️ Far off.")

        if not won:
            print("\n💀 Out of attempts.")
            print(f"The number was {number}.")
            if guess_history:
                print("📜 Your guesses:", ", ".join(map(str, guess_history)))
            print(f"❌ You used all {max_attempts} attempts.")
        else:
            print(f"🏆 You solved it in {attempts} guesses.")

        again = get_choice(
            prompt="\n🔄 Play again? (y/n): ",
            choices=['y', 'yes', 'n', 'no'],
            error_invalid="⚠️ Invalid choice. Please enter 'y' or 'n'."
        )

        if again in ['n', 'no']:
            print("👋 Goodbye.")
            break


if __name__ == "__main__":
    if len(sys.argv) > 1:
        random.seed(int(sys.argv[1]))
    main()
