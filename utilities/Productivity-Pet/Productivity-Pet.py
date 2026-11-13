import random
import json
import os
from datetime import datetime

SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "save.json")


def _calculate_task_rewards(tasks, pet_class):
    """Return completed count, completed names, and earned XP in task order."""
    completed_task_list = []
    total_xp = 0

    for task in tasks:
        if not task["done"]:
            continue

        completed_task_list.append(task["name"])
        if task["difficulty"] == "easy":
            xp = 5
        elif task["difficulty"] == "medium":
            xp = 15
        else:
            xp = 30
        if pet_class == "Dragon 🐉" and task["difficulty"] == "hard":
            xp += 10
        total_xp += xp

    return len(completed_task_list), total_xp, completed_task_list


def main():
    print("🐦‍🔥 PRODUCTIVITY PET 🐦‍🔥")
    print("Track your tasks and evolve your pet!\n")

    # =========================
    # LOAD SAVE DATA
    # =========================

    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as file:
            data = json.load(file)
    else:
        data = {
            "xp": 0,
            "level": 1,
            "coins": 0,
            "streak": 0,
            "best_streak": 0,
            "completed_tasks": 0,
            "achievements": [],
            "pet_class": "",
            "last_day": "",
            "history": []
        }

    # =========================
    # FIRST TIME PET CLASS
    # =========================

    if data["pet_class"] == "":
        print("Choose your pet class:\n")
        print("1. 🐉 Dragon  → Extra XP from hard tasks")
        print("2. 🦊 Fox     → Extra coins")
        print("3. 🦉 Owl     → Streak protection")

        choice = input("\n➡️ Choose your class (1/2/3): ").strip()

        if choice == "1":
            data["pet_class"] = "Dragon 🐉"
        elif choice == "2":
            data["pet_class"] = "Fox 🦊"
        else:
            data["pet_class"] = "Owl 🦉"

        with open(SAVE_FILE, "w") as file:
            json.dump(data, file, indent=4)

    # =========================
    # MAIN LOOP
    # =========================

    while True:

        print("\n╔════════════════════════════╗")
        print("║      PRODUCTIVITY PET      ║")
        print("╚════════════════════════════╝")

        print(f"\nClass: {data['pet_class']}")
        print(f"⭐ Level: {data['level']}")
        print(f"✨ XP: {data['xp']}")
        print(f"🪙 Coins: {data['coins']}")
        print(f"🔥 Streak: {data['streak']}")
        print(f"🏆 Best Streak: {data['best_streak']}")
        print(f"✅ Total Tasks: {data['completed_tasks']}")
        print(f"🏅 Achievements: {len(data['achievements'])}")

        # Show recent history summary
        if data["history"]:
            print(f"\n📖 Recent Activity: {len(data['history'])} day(s)")

        user = input(
            "\n➡️ Did you complete your tasks today? (yes/no): "
        ).lower().strip()

        if user in ["yes", "yeah", "yep", "y"]:

            count = input(
                "\n📝 How many tasks were in your list? "
            ).strip()

            if not count.isdigit() or int(count) <= 0:
                print("⚠️ Please enter a valid number.\n")
                continue

            count = int(count)

            tasks = []

            for i in range(count):

                print(f"\n📌 Task {i+1}")
                task = input("   Task Name: ").strip()

                difficulty = input(
                    "   Difficulty (easy/medium/hard): "
                ).lower().strip()

                if difficulty not in ["easy", "medium", "hard"]:
                    difficulty = "easy"

                done_input = input(
                    "   Completed? (yes/no): "
                ).lower().strip()

                done = done_input in ["yes", "y"]

                task_data = {
                    "name": task,
                    "difficulty": difficulty,
                    "done": done
                }

                tasks.append(task_data)

            completed, total_xp, completed_task_list = _calculate_task_rewards(
                tasks, data["pet_class"]
            )
            percentage = (completed / count) * 100 if count > 0 else 0
            print(f"\n📊 Progress: {percentage:.1f}%")

            # =========================
            # MOOD SYSTEM
            # =========================

            if percentage >= 90:
                mood = "😄 Motivated"
            elif percentage >= 70:
                mood = "😊 Happy"
            elif percentage >= 40:
                mood = "😐 Neutral"
            else:
                mood = "😴 Lazy"

            print(f"💭 Pet Mood: {mood}")

            # =========================
            # REWARDS & PROGRESSION
            # =========================

            data["xp"] += total_xp
            data["completed_tasks"] += completed
            new_level = (data["xp"] // 100) + 1
            if new_level > data["level"]:
                print(f"\n⬆️ LEVEL UP! You reached Level {new_level}!")
            data["level"] = new_level

            if data["xp"] >= 800:
                pet_stage = "🦅 Legendary Phoenix"
            elif data["xp"] >= 400:
                pet_stage = "🐦‍🔥 Adult"
            elif data["xp"] >= 150:
                pet_stage = "🐤 Teen"
            elif data["xp"] >= 50:
                pet_stage = "🐣 Baby"
            else:
                pet_stage = "🥚 Egg"

            print(f"🐾 Current Pet Stage: {pet_stage}")

            earned_coins = completed * 5
            if data["pet_class"] == "Fox 🦊":
                earned_coins += 10

            data["coins"] += earned_coins

            print(f"✨ XP Earned: +{total_xp}")
            print(f"🪙 Coins Earned: +{earned_coins}")

            # =========================
            # TASK HISTORY
            # =========================

            today_str = datetime.now().strftime("%Y-%m-%d")
            history_entry = {
                "date": today_str,
                "total_tasks": count,
                "completed": completed,
                "percentage": round(percentage, 1),
                "tasks": completed_task_list[:8]
            }

            data["history"] = [h for h in data["history"] if h["date"] != today_str]
            data["history"].append(history_entry)
            data["history"] = sorted(data["history"], key=lambda x: x["date"], reverse=True)[:7]

            # =========================
            # STREAK, ACHIEVEMENTS, WEEKLY BOSS, EVENTS...
            # =========================

            today = datetime.now().strftime("%Y-%m-%d")

            if data["last_day"] != today:
                if percentage >= 65:
                    data["streak"] += 1
                else:
                    if data["pet_class"] == "Owl 🦉" and data["streak"] > 0:
                        print("🦉 Owl protected your streak!")
                    else:
                        data["streak"] = 0

            data["last_day"] = today

            if data["streak"] > data["best_streak"]:
                data["best_streak"] = data["streak"]

            # Achievements
            if completed >= 1 and "🥚 First Steps" not in data["achievements"]:
                data["achievements"].append("🥚 First Steps")
                print("\n🏆 Achievement Unlocked: 🥚 First Steps")

            if data["streak"] >= 7 and "🔥 On Fire" not in data["achievements"]:
                data["achievements"].append("🔥 On Fire")
                print("\n🏆 Achievement Unlocked: 🔥 On Fire")

            if data["completed_tasks"] >= 50 and "⚡ Workhorse" not in data["achievements"]:
                data["achievements"].append("⚡ Workhorse")
                print("\n🏆 Achievement Unlocked: ⚡ Workhorse")

            if percentage >= 95 and "👑 Legendary Focus" not in data["achievements"]:
                data["achievements"].append("👑 Legendary Focus")
                print("\n🏆 Achievement Unlocked: 👑 Legendary Focus")

            # Weekly boss
            print("\n🐉 WEEKLY BOSS - Complete 15 tasks in one session")
            if completed >= 15:
                print("🎉 Boss defeated!")
                print("🎁 Reward: +100 XP and +50 Coins")
                data["xp"] += 100
                data["coins"] += 50
            else:
                print(f"⚔️ Progress: {completed}/15")

            # Random events
            if random.randint(1, 100) <= 30:
                events = [
                    "🎁 Your pet found treasure! +25 Coins",
                    "✨ Lucky productivity boost! +40 XP",
                    "🍀 Your pet feels inspired! +1 Streak"
                ]
                event = random.choice(events)
                print(f"\n{event}")

                if "Coins" in event:
                    data["coins"] += 25
                elif "XP" in event:
                    data["xp"] += 40
                elif "Streak" in event:
                    data["streak"] += 1

            # =========================
            # SAVE PROGRESS
            # =========================

            with open(SAVE_FILE, "w") as file:
                json.dump(data, file, indent=4)

            print("\n🏆 Amazing work today!\n")

        elif user in ["no", "nope", "nah", "n"]:
            print("💬 No worries! Come back stronger tomorrow.\n")

        else:
            print("⚠️ Please answer yes or no.\n")
            continue

        again = input(
            "🔄 Track another day? (y/n): "
        ).lower().strip()

        if again != "y":
            break

    print("\n👋 Thanks for using Productivity Pet! Keep levelling up your companion!🐦‍🔥")


if __name__ == "__main__":
    main()
