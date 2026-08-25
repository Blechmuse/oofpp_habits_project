"""Application service for habit operations."""

from datetime import datetime

from checkin import CheckIn
from database import Database
from habit import Habit, Period


class HabitManager:
    """Coordinates domain objects and SQLite persistence."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def create_habit(self, name: str, description: str, period: Period) -> Habit:
        """Create and persist a habit."""
        if not name.strip():
            raise ValueError("Habit name cannot be empty")
        return self.database.insert_habit(Habit(None, name.strip(), description.strip(), period, datetime.now()))

    def update_habit(self, habit_id: int, name: str, description: str, period: Period) -> Habit:
        """Update and return a habit."""
        habit = self.get_habit(habit_id)
        if habit is None:
            raise ValueError("Habit not found")
        if not name.strip():
            raise ValueError("Habit name cannot be empty")
        habit.name, habit.description, habit.period = name.strip(), description.strip(), period
        self.database.update_habit(habit)
        return habit

    def delete_habit(self, habit_id: int) -> None:
        """Delete a habit."""
        if self.get_habit(habit_id) is None:
            raise ValueError("Habit not found")
        self.database.delete_habit(habit_id)

    def complete_habit(self, habit_id: int) -> CheckIn:
        """Record a completion for an existing habit."""
        if self.get_habit(habit_id) is None:
            raise ValueError("Habit not found")
        return self.database.insert_checkin(CheckIn(None, habit_id, datetime.now()))

    def list_habits(self) -> list[Habit]:
        """Return all habits."""
        return self.database.load_habits()

    def get_habit(self, habit_id: int) -> Habit | None:
        """Return a habit by ID."""
        return self.database.load_habit(habit_id)

