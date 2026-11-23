import random


def roll_dice() -> tuple[int, int]:
    """Roll two six-sided dice and return (die1, die2)."""
    return random.randint(1, 6), random.randint(1, 6)


def main():
    global choice, dice_emoji, num1, num2
    print("🎲 Dice Rolling Game! 🎲")
    print("Roll two dice and see what you get!\n")

    dice_emoji = {
        1: '⚀',
        2: '⚁',
        3: '⚂',
        4: '⚃',
        5: '⚄',
        6: '⚅'
    }


    while True:
        choice = input("🎲 Roll the dice? (y/n): ").lower()

        if choice == "y":
            num1, num2 = roll_dice()
            print("\n🎲 Rolling...")
            print(f"Dice 1: {num1} {dice_emoji[num1]}")
            print(f"Dice 2: {num2} {dice_emoji[num2]}")
            print(f"📊 Total: {num1 + num2}\n")

        elif choice == "n":
            print("\n👋 Thanks for playing! See you next time!\n")
            break

        else:
            print("❌ Invalid input!! Please enter 'y' or 'n'.\n")

if __name__ == '__main__':
    main()
