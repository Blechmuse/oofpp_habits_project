"""Functional analytics over persisted habit data."""

from datetime import date, timedelta
from functools import reduce

from database import Database
from habit import Habit, Period


def get_all_habits(database: Database) -> list[Habit]:
    """Return all habits from SQLite."""
    return database.load_habits()


def get_habits_by_period(database: Database, period: Period) -> list[Habit]:
    """Filter habits by period using a pure predicate."""
    return list(filter(lambda habit: habit.period is period, get_all_habits(database)))


def get_longest_streak_habit(database: Database, habit_id: int) -> int:
    """Return the longest consecutive completion streak for one habit."""
    habit = database.load_habit(habit_id)
    if habit is None:
        return 0
    checkins = database.load_checkins(habit_id)
    keys = sorted({_period_key(checkin.completed_at.date(), habit.period) for checkin in checkins})
    if not keys:
        return 0

    def extend(current: tuple[int, int, object], key: object) -> tuple[int, int, object]:
        current_length, longest_length, previous = current
        next_length = current_length + 1 if key == _next_key(previous, habit.period) else 1
        return next_length, max(longest_length, next_length), key

    result = reduce(extend, keys[1:], (1, 1, keys[0]))
    return result[1]


def get_longest_streak_all(database: Database) -> int:
    """Return the largest streak among all habits."""
    return max(map(lambda habit: get_longest_streak_habit(database, habit.id or 0), get_all_habits(database)), default=0)


def _period_key(completed: date, period: Period) -> date:
    return completed if period is Period.DAILY else completed - timedelta(days=completed.weekday())


def _next_key(previous: object, period: Period) -> object:
    return previous + timedelta(days=1 if period is Period.DAILY else 7)
