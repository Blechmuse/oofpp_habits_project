"""Menu-driven command-line interface."""

from analytics import (
    get_all_habits,
    get_habits_by_period,
    get_longest_streak_habit,
)
from database import Database
from habit import Habit, Period
from habitmanager import HabitManager


class CLI:
    """Handles user input and presents habit tracking actions."""

    def __init__(self, manager: HabitManager, database: Database) -> None:
        self.manager = manager
        self.database = database

    def run(self) -> None:
        """Run until the user chooses Exit."""
        actions = {
            "1": self.show_all,
            "2": self.show_by_period,
            "3": self.create,
            "4": self.edit,
            "5": self.delete,
            "6": self.complete,
            "7": self.analytics_menu,
        }
        while True:
            print("\nHabit Tracker")
            print("1. Show all habits\n2. Show habits by periodicity\n3. Create habit")
            print("4. Edit habit\n5. Delete habit\n6. Complete habit\n7. Analytics\n8. Exit")
            choice = input("Choose an option: ").strip()
            if choice == "8":
                return
            action = actions.get(choice)
            if action:
                try:
                    action()
                except (ValueError, TypeError) as error:
                    print(f"Error: {error}")
            else:
                print("Invalid option.")

    def show_all(self) -> None:
        """Print every habit."""
        self._print_habits(self.manager.list_habits())

    def show_by_period(self) -> None:
        """Print habits matching a selected period."""
        self._print_habits(get_habits_by_period(self.database, self._read_period()))

    def create(self) -> None:
        """Prompt for and create a habit."""
        habit = self.manager.create_habit(input("Name: "), input("Description: "), self._read_period())
        print(f"Created habit #{habit.id}.")

    def edit(self) -> None:
        """Prompt for and edit a habit."""
        habit_id = int(input("Habit ID: "))
        habit = self.manager.update_habit(habit_id, input("Name: "), input("Description: "), self._read_period())
        print(f"Updated habit #{habit.id}.")

    def delete(self) -> None:
        """Prompt for and delete a habit."""
        habit_id = int(input("Habit ID: "))
        self.manager.delete_habit(habit_id)
        print("Habit deleted.")

    def complete(self) -> None:
        """Prompt for and complete a habit."""
        checkin = self.manager.complete_habit(int(input("Habit ID: ")))
        print(f"Completed at {checkin.completed_at:%Y-%m-%d %H:%M:%S}.")

    def analytics_menu(self) -> None:
        """Run an analytics submenu."""
        print("1. List all habits\n2. List habits with same periodicity")
        print("3. Longest streak of all habits\n4. Longest streak of a selected habit")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            self._print_habits(get_all_habits(self.database))
        elif choice == "2":
            self._print_habits(get_habits_by_period(self.database, self._read_period()))
        elif choice == "3":
            habits = get_all_habits(self.database)
            longest_habit = max(
                habits,
                key=lambda habit: get_longest_streak_habit(self.database, habit.id or 0),
                default=None,
            )
            if longest_habit is None:
                print("Longest streak: 0 (no habits)")
            else:
                streak = get_longest_streak_habit(self.database, longest_habit.id or 0)
                print(f"Longest streak: {streak} ({longest_habit.name})")
        elif choice == "4":
            habit_id = int(input("Habit ID: "))
            habit = self.manager.get_habit(habit_id)
            if habit is None:
                print("Habit not found.")
            else:
                streak = get_longest_streak_habit(self.database, habit_id)
                print(f"Longest streak: {streak} ({habit.name})")
        else:
            print("Invalid option.")

    @staticmethod
    def _read_period() -> Period:
        periods = {"1": Period.DAILY, "2": Period.WEEKLY}
        while True:
            print("1. Daily\n2. Weekly")
            choice = input("Choose period: ").strip()
            if choice in periods:
                return periods[choice]
            print("Invalid choice. Please select 1 or 2.")

    @staticmethod
    def _print_habits(habits: list[Habit]) -> None:
        if not habits:
            print("No habits found.")
            return
        for habit in habits:
            print(f"#{habit.id} {habit.name} [{habit.period.value}] - {habit.description}")
