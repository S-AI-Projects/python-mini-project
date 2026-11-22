import random
import time
import os
import sys
import threading

# Note: Works best in a terminal. Browser version (Pyodide) uses simplified input.

EMOJIS = ["🍎", "🚗", "⚽", "🐍", "🎧", "🔥", "🌈", "🚀"]
HIGH_SCORE_FILE = "highscore.txt"

DIFFICULTY_TIME_LIMITS = {
    "1": 5,   # Easy   - memorise time
    "2": 4,   # Medium - memorise time
    "3": 2,   # Hard   - memorise time
}

DIFFICULTY_INPUT_LIMITS = {
    "1": 10,  # Easy   - input time
    "2": 8,   # Medium - input time
    "3": 5,   # Hard   - input time
}


# Detect if running in browser (Pyodide)
def is_browser() -> bool:
    """Return True if running in a browser environment (Pyodide / Emscripten).

    Contract and Mutation Protection:
    - Inputs: None (takes 0 arguments; inspects `sys.platform`).
    - Result: `bool` (`True` if and only if `sys.platform == 'emscripten'`, otherwise `False`).
    - Protected Condition: Exact equality against the Emscripten WebAssembly runtime platform tag.
    - Fixture Anchors:
        - `EMOJIS = [...]` (line 9)
        - `DIFFICULTY_TIME_LIMITS = {...}` (line 12)
    - Observable Mutation: None (pure predicate, zero mutation).
    """
    return sys.platform == "emscripten"


# Core, testable logic (no I/O, no global state)

def get_time_limit(choice):
    """Return the memorise display time (seconds) for a difficulty choice."""
    return DIFFICULTY_TIME_LIMITS.get(choice, 4)


def get_input_limit(choice):
    """Return the allowed input time (seconds) for a difficulty choice."""
    return DIFFICULTY_INPUT_LIMITS.get(choice, 8)


def generate_sequence(emojis, level):
    """Generate a random emoji sequence for the given level."""
    if level < 1:
        raise ValueError("level must be >= 1")
    return random.choices(emojis, k=level + 2)


def parse_input(raw_input):
    """Turn raw user text into a list of emoji tokens."""
    return [token.strip() for token in raw_input.split() if token.strip()]


def validate_input(user_sequence, correct_sequence):
    """Return True if the user's sequence exactly matches the correct one."""
    return user_sequence == correct_sequence


def is_timeout(elapsed_seconds, time_limit):
    """Return True if elapsed_seconds exceeds the allowed time_limit."""
    return elapsed_seconds > time_limit


def update_streak(is_correct, current_streak):
    """Increment streak on a correct round, reset to 0 on an incorrect one."""
    return current_streak + 1 if is_correct else 0


def format_countdown_message(remaining_seconds):
    """Return the display string for a given number of seconds left."""
    if remaining_seconds <= 0:
        return "⏱️  Time's up!"
    return f"⏱️  {remaining_seconds}s left..."


def calculate_score(level, streak):
    """Calculate score for a correctly-answered round."""
    base = level * 10
    streak_bonus = streak * 2
    return base + streak_bonus


# I/O helpers

def load_high_score():
    if not os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, "w", encoding="utf-8") as file:
                file.write("0")
        except OSError as e:
            print(f"⚠️ Warning: Could not initialize high score file: {e}")

    try:
        with open(HIGH_SCORE_FILE, "r", encoding="utf-8") as file:
            return int(file.read().strip() or "0")
    except (FileNotFoundError, ValueError, OSError) as e:
        print(f"⚠️ Warning: Could not read high score file: {e}")
        return 0


def save_high_score(score):
    try:
        with open(HIGH_SCORE_FILE, "w", encoding="utf-8") as file:
            file.write(str(score))
    except OSError as e:
        print(f"⚠️ Could not save high score: {e}")


def clear_screen():
    """Safe clear screen that works in both terminal and browser."""
    if is_browser():
        print("\n" * 3)  # Simple spacing for browser
    else:
        os.system('cls' if os.name == 'nt' else 'clear')


def run_countdown(duration, stop_event):
    """Original fancy countdown (terminal only)."""
    remaining = duration
    while remaining > 0:
        if stop_event.wait(timeout=1):
            return
        remaining -= 1
        sys.stdout.write("\0337")
        sys.stdout.write("\033[2A")
        sys.stdout.write("\r\033[2K")
        sys.stdout.write(format_countdown_message(remaining))
        sys.stdout.write("\0338")
        sys.stdout.flush()


# Game loop

def main():
    high_score = load_high_score()

    while True:
        print("\n🎮 Welcome to Emoji Memory Game!")
        print(f"🏅 High Score: {high_score}\n")

        print("🎯 Select Difficulty")
        print("1. Easy (5 sec)")
        print("2. Medium (4 sec)")
        print("3. Hard (2 sec)")

        while True:
            choice = input("Enter choice (1/2/3): ").strip()
            if choice in DIFFICULTY_TIME_LIMITS:
                break
            print("⚠️ Invalid input. Enter 1, 2, or 3.")

        display_time = get_time_limit(choice)
        input_time = get_input_limit(choice)

        print("\n⏳ Get Ready!")
        for i in range(3, 0, -1):
            print(i)
            time.sleep(1)
        clear_screen()

        score = 0
        level = 1
        streak = 0

        # Gameplay Loop
        while True:
            sequence = generate_sequence(EMOJIS, level)

            print("🧠 MEMORIZE THESE EMOJIS:")
            print(" ".join(sequence))

            time.sleep(display_time)
            clear_screen()

            # Input Phase
            print(format_countdown_message(input_time))
            print("Type the emojis in order (separated by spaces):")
            sys.stdout.write("> ")
            sys.stdout.flush()

            if is_browser():
                # Simplified version for browser (no threads/ANSI)
                print("\n⚠️ Browser mode active - enter your answer below.")
                start_time = time.time()
                user_input_raw = input().strip()
                elapsed = time.time() - start_time
            else:
                # Original fancy terminal version
                stop_event = threading.Event()
                timer_thread = threading.Thread(
                    target=run_countdown, args=(
                        input_time, stop_event), daemon=True
                )
                timer_thread.start()

                start_time = time.time()
                user_input_raw = input().strip()
                elapsed = time.time() - start_time

                stop_event.set()
                timer_thread.join(timeout=0.2)

            user_input = parse_input(user_input_raw)
            timed_out = is_timeout(elapsed, input_time)

            if not user_input:
                print("⚠️ Empty input detected!")
                print("❌ Wrong!")
                print("Correct sequence was:", " ".join(sequence))
                break

            correct = validate_input(user_input, sequence) and not timed_out

            streak = update_streak(correct, streak)

            if correct:
                score += calculate_score(level, streak)
                print("✅ Correct!")
                level += 1
                print(f"🏆 Score: {score}")
                print(f"🔥 Streak: {streak}\n")
            else:
                if timed_out:
                    print("⏱️ Time's up!")
                print("❌ Wrong!")
                print("Correct sequence was:", " ".join(sequence))
                print(f"🔥 Streak: {streak}")
                break

        # Game Over Processing
        print("\n🎯 Game Over!")
        print(f"🏆 Final Score: {score}")

        if score > high_score:
            print("🔥 NEW HIGH SCORE!")
            high_score = score
            save_high_score(score)
        else:
            print(f"🏅 High Score remains: {high_score}")

        # Replay Loop
        play_again = False
        while True:
            replay = input("\nPlay again? (y/n): ").strip().lower()
            if replay in ['y', 'yes']:
                play_again = True
                break
            elif replay in ['n', 'no']:
                play_again = False
                break
            print("⚠️ Invalid input. Please enter 'y' or 'n'.")

        if not play_again:
            print("👋 Thanks for playing!")
            break


if __name__ == '__main__':
    main()
