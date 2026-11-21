def main():
    """Execute the interactive FLAMES relationship calculation game.

    Workflow Overview
    -----------------
    1. Input Validation: Prompts for two non-empty alphabetic names.
    2. Character Cancellation: Removes shared characters one-by-one from both names.
    3. Degenerate Detection: If remaining letters count == 0, flags as undefined.
    4. Decisive State Transition (Cyclic Elimination):
       Starting with the full relationship list:
           flames = ['F', 'L', 'A', 'M', 'E', 'S']
       repeatedly steps through using modulo arithmetic:
           index = (index + count - 1) % len(flames)
           flames.pop(index)
       until exactly one letter remains.
    5. Scoring & Reporting: Computes a compatibility percentage from matched
       characters and prints the relationship card plus session statistics.

    Worked Example: Smallest Valid Input
    -----------------------------------
    Trace of main() using the smallest valid input (names: "a" and "b", choice: "n").

    Source Anchors / Preconditions:
      - Line 5:  session = {"rounds": 0, "results": {r: 0 for r in "FLAMES"}, "total_score": 0}
      - Line 34: name1 input = "a" ('a'.isalpha() is True)
      - Line 41: name2 input = "b" ('b'.isalpha() is True)
      - Line 49: name1_list = ['a']
      - Line 50: name2_list = ['b']
      - Line 52: Common letter cancellation: 'a' not in ['b'] -> no removals.
      - Line 57: count = len(['a']) + len(['b']) = 2
      - Line 73: total_len = 2, matched_chars = 0
      - Line 75: score = 30 + round((0 / 2) * 70) = 30%
      - Line 80: flames = ['F', 'L', 'A', 'M', 'E', 'S'] (anchor)

    Decisive State Transition:
      With count = 2, cyclic elimination proceeds as follows:
        Round 1: len=6, index=(0 + 2 - 1)%6 = 1 -> 'L' popped -> ['F', 'A', 'M', 'E', 'S'], next index=1
        Round 2: len=5, index=(1 + 2 - 1)%5 = 2 -> 'M' popped -> ['F', 'A', 'E', 'S'],      next index=2
        Round 3: len=4, index=(2 + 2 - 1)%4 = 3 -> 'S' popped -> ['F', 'A', 'E'],           next index=3
        Round 4: len=3, index=(3 + 2 - 1)%3 = 1 -> 'A' popped -> ['F', 'E'],                next index=1
        Round 5: len=2, index=(1 + 2 - 1)%2 = 0 -> 'F' popped -> ['E'],                      next index=0
      The decisive elimination leaves flames = ['E'].
      Result: 'E' -> Enemies 😈, Rivalry Quotient: 30%.

    Worked Example: Ordinary Input ("alex", "emma", "n")
    ----------------------------------------------------
    Source Anchors / Preconditions:
      - Line 34: name1 = "alex", Line 41: name2 = "emma"
      - Line 52: Common letters 'a' and 'e' cancelled.
      - Line 57: Remaining letters: ['l', 'x'] and ['m', 'm'] -> count = 4.
      - Line 73: total_len = 8, matched_chars = 4.
      - Line 75: score = 30 + round((4 / 8) * 70) = 65%.
      - Line 80: flames = ['F', 'L', 'A', 'M', 'E', 'S']
    Decisive State Transition:
      With count = 4, cyclic elimination proceeds:
        Round 1: len=6, index=(0 + 4 - 1)%6 = 3 -> 'M' popped -> ['F', 'L', 'A', 'E', 'S'], next index=3
        Round 2: len=5, index=(3 + 4 - 1)%5 = 1 -> 'L' popped -> ['F', 'A', 'E', 'S'],      next index=1
        Round 3: len=4, index=(1 + 4 - 1)%4 = 0 -> 'F' popped -> ['A', 'E', 'S'],           next index=0
        Round 4: len=3, index=(0 + 4 - 1)%3 = 0 -> 'A' popped -> ['E', 'S'],                next index=0
        Round 5: len=2, index=(0 + 4 - 1)%2 = 1 -> 'S' popped -> ['E'],                      next index=1
      Result: 'E' -> Enemies 😈, Rivalry Quotient: 65%.
    """
    global char, choice, count, final, flames, index, mapping, matched_chars, name1, name1_list, name2, name2_list, original_name1, original_name2, result, score, share_text, total_len, valid_game

    # Session statistics tracker
    session = {
        "rounds": 0,
        "results": {r: 0 for r in "FLAMES"},
        "total_score": 0,
    }

    mapping = {
        'F': {"rel": "Friends",  "emoji": "🤝", "metric": "Bond Strength"},
        'L': {"rel": "Love",     "emoji": "❤️", "metric": "Compatibility Score"},
        'A': {"rel": "Affection","emoji": "😊", "metric": "Crush Intensity"},
        'M': {"rel": "Marriage", "emoji": "💍", "metric": "Marital Bliss"},
        'E': {"rel": "Enemies",  "emoji": "😈", "metric": "Rivalry Quotient"},
        'S': {"rel": "Siblings", "emoji": "🏠", "metric": "Nuisance Factor"},
    }

    while True:
        print("\n" + "=" * 50)
        print("🔥 FLAMES GAME - FIND YOUR RELATIONSHIP STATUS! 🔥")
        print("=" * 50)
        print("\nF - Friends 🤝")
        print("L - Love ❤️")
        print("A - Affection 😊")
        print("M - Marriage 💍")
        print("E - Enemies 😈")
        print("S - Siblings 🏠")
        print("=" * 50)

        # Get first name
        while True:
            name1 = input("\nEnter first name: ").strip().lower().replace(" ", "")
            if name1.isalpha():
                break
            print("⚠️ Error: Name must contain only alphabets and cannot be empty! Please try again.")

        # Get second name
        while True:
            name2 = input("Enter second name: ").strip().lower().replace(" ", "")
            if name2.isalpha():
                break
            print("⚠️ Error: Name must contain only alphabets and cannot be empty! Please try again.")

        original_name1 = name1
        original_name2 = name2

        name1_list = list(name1)
        name2_list = list(name2)

        for char in name1_list[:]:
            if char in name2_list:
                name1_list.remove(char)
                name2_list.remove(char)

        count = len(name1_list) + len(name2_list)

        # FIX: Use a flag to track if we should calculate the game results
        valid_game = True

        if count == 0:
            print("\n" + "=" * 50)
            print("🚨 DEGENERATE CASE DETECTED! 🚨")
            print("=" * 50)
            print("\nThese names share all letters! FLAMES is undefined.")
            print("Please try with different names for a meaningful result.")
            print("=" * 50)
            valid_game = False  # Set flag to False so we skip the game calculation

        # Only run game calculations if it's a valid match
        if valid_game:
            total_len = len(original_name1) + len(original_name2)
            matched_chars = total_len - count
            score = 30 + round((matched_chars / total_len) * 70) if total_len > 0 else 0

            print("\nAfter removing common letters:")
            print(f"Remaining letters: {count}")

            flames = ['F', 'L', 'A', 'M', 'E', 'S']
            index = 0
            while len(flames) > 1:
                index = (index + count - 1) % len(flames)
                flames.pop(index)

            result = flames[0]
            final = mapping[result]

            # Update session statistics
            session["rounds"] += 1
            session["results"][result] += 1
            session["total_score"] += score

            print("\n" + "=" * 50)
            print("📝 MATCH REPORT CARD")
            print("=" * 50)
            print(f"\nNames: {original_name1.capitalize()} & {original_name2.capitalize()}")
            print(f"Status: {final['emoji']} {final['rel'].upper()} {final['emoji']}")
            print(f"{final['metric']}: {score}%")
            print("\n" + "=" * 50)
        
            share_text = (f"✨ FLAMES Match Report ✨\n"
                          f"{original_name1.capitalize()} + {original_name2.capitalize()}\n"
                          f"Result: {final['rel']} {final['emoji']}\n"
                          f"{final['metric']}: {score}%")

            print("📋 COPY TO SHARE:")
            print(share_text)
            print("=" * 50)

        # The loop safely lands here now, even for degenerate cases!
        while True:
            choice = input("\n🔄 Do you want to play again? (y/n): ").lower().strip()
            if choice in ('y', 'yes', 'n', 'no'):
                break
            print("⚠️ Invalid choice. Please enter 'y' or 'n'.")

        if choice in ('n', 'no'):
            # Display session statistics on exit
            if session["rounds"] > 0:
                avg = session["total_score"] / session["rounds"]
                top = max(session["results"], key=session["results"].get)
                print("\n" + "=" * 50)
                print("📊 SESSION STATS")
                print("=" * 50)
                print(f"  Total Rounds Played : {session['rounds']}")
                print("-" * 50)
                for letter, count in session["results"].items():
                    label = mapping[letter]["rel"]
                    bar   = "█" * session["results"][letter]
                    print(f"  {label:<12}: {count:>2}  {bar}")
                print("-" * 50)
                print(f"  Most Common Result  : {mapping[top]['rel']} {mapping[top]['emoji']}")
                print(f"  Avg Score           : {avg:.1f}%")
                print("=" * 50)
            print("\n👋 Thanks for playing FLAMES! Goodbye!")
            break

if __name__ == '__main__':
    main()
