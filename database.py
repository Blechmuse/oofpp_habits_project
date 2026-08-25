"""SQLite persistence for habits and check-ins."""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from checkin import CheckIn
from habit import Habit, Period


class Database:
    """Repository for the application's SQLite data."""

    def __init__(self, path: str | Path = "habits.db") -> None:
        self.path = str(path)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.create_tables()

    def create_tables(self) -> None:
        """Create tables and indexes when they do not exist."""
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                period TEXT NOT NULL CHECK (period IN ('daily', 'weekly')),
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS checkins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL REFERENCES habits(id) ON DELETE CASCADE,
                completed_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_checkins_habit ON checkins(habit_id);
            """
        )
        self.connection.commit()

    def insert_habit(self, habit: Habit) -> Habit:
        """Insert a habit and return it with its generated ID."""
        cursor = self.connection.execute(
            "INSERT INTO habits (name, description, period, created_at) VALUES (?, ?, ?, ?)",
            (habit.name, habit.description, habit.period.value, habit.created_at.isoformat()),
        )
        self.connection.commit()
        habit.id = cursor.lastrowid
        return habit

    def update_habit(self, habit: Habit) -> None:
        """Persist editable fields of an existing habit."""
        if habit.id is None:
            raise ValueError("Cannot update a habit without an ID")
        self.connection.execute(
            "UPDATE habits SET name = ?, description = ?, period = ? WHERE id = ?",
            (habit.name, habit.description, habit.period.value, habit.id),
        )
        self.connection.commit()

    def delete_habit(self, habit_id: int) -> None:
        """Delete a habit and its associated check-ins."""
        self.connection.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
        self.connection.commit()

    def load_habits(self) -> list[Habit]:
        """Load all habits ordered by ID."""
        rows = self.connection.execute("SELECT * FROM habits ORDER BY id").fetchall()
        return [self._habit_from_row(row) for row in rows]

    def load_habit(self, habit_id: int) -> Habit | None:
        """Load one habit by ID."""
        row = self.connection.execute("SELECT * FROM habits WHERE id = ?", (habit_id,)).fetchone()
        return self._habit_from_row(row) if row else None

    def insert_checkin(self, checkin: CheckIn) -> CheckIn:
        """Insert a completion and return it with its generated ID."""
        cursor = self.connection.execute(
            "INSERT INTO checkins (habit_id, completed_at) VALUES (?, ?)",
            (checkin.habit_id, checkin.completed_at.isoformat()),
        )
        self.connection.commit()
        checkin.id = cursor.lastrowid
        return checkin

    def load_checkins(self, habit_id: int | None = None) -> list[CheckIn]:
        """Load check-ins, optionally restricted to one habit."""
        if habit_id is None:
            rows = self.connection.execute("SELECT * FROM checkins ORDER BY completed_at").fetchall()
        else:
            rows = self.connection.execute(
                "SELECT * FROM checkins WHERE habit_id = ? ORDER BY completed_at", (habit_id,)
            ).fetchall()
        return [CheckIn(row["id"], row["habit_id"], datetime.fromisoformat(row["completed_at"])) for row in rows]

    def initialize_default_data(self) -> None:
        """Seed five habits and four weeks of example completions once."""
        if self.connection.execute("SELECT 1 FROM habits LIMIT 1").fetchone():
            return

        now = datetime.now().replace(microsecond=0)
        # fixture_start marks the beginning of the four-week test period.
        fixture_start = now - timedelta(days=27)
        defaults = [
            ("Morning exercise", "Move for at least 20 minutes", Period.DAILY),
            ("Read", "Read a book", Period.DAILY),
            ("Meal planning", "Plan meals for the week", Period.WEEKLY),
            ("Weekly review", "Reflect on the past week", Period.WEEKLY),
            ("Drink water", "Drink eight glasses of water", Period.DAILY),
        ]
        habits = [
            self.insert_habit(Habit(None, name, description, period, fixture_start))
            for name, description, period in defaults
        ]
        daily_days = {
            "Morning exercise": range(28),
            "Read": (*range(14), 27),
            "Drink water": (0, 1, 2, 5, 6, 9, 10, 11, 12, 16, 17, 22, 24, 27),
        }
        weekly_weeks = {
            "Meal planning": range(4),
            "Weekly review": (0, 1, 3),
        }

        # Intentional gaps provide interrupted streaks for analytics tests.
        for habit in habits:
            if habit.id is None:
                continue

            if habit.period is Period.DAILY:
                for day in daily_days[habit.name]:
                    completed_at = fixture_start + timedelta(days=day)
                    self.insert_checkin(CheckIn(None, habit.id, completed_at))
            else:
                for week in weekly_weeks[habit.name]:
                    completed_at = fixture_start + timedelta(weeks=week)
                    self.insert_checkin(CheckIn(None, habit.id, completed_at))

    def close(self) -> None:
        """Close the SQLite connection."""
        self.connection.close()

    @staticmethod
    def _habit_from_row(row: sqlite3.Row) -> Habit:
        return Habit(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            period=Period(row["period"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )
