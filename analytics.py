"""Functional analytics over persisted habit data."""

from datetime import date, timedelta
from functools import reduce

from checkin import CheckIn
from habit import Habit, Period


def get_all_habits(habits: list[Habit]) -> list[Habit]:
    """Return all supplied habits."""
    return list(habits)


def get_habits_by_period(habits: list[Habit], period: Period) -> list[Habit]:
    """Return habits matching the selected periodicity."""
    return list(filter(lambda habit: habit.period is period, habits))


def calculate_longest_streak(checkins: list[CheckIn], period: Period) -> int:
    """Calculate the longest consecutive streak."""
    # A set removes duplicate check-ins; normalizing first makes weekly
    # completions comparable even when they fall on different weekdays.
    keys = sorted(
        {_period_key(checkin.completed_at.date(), period) for checkin in checkins}
    )
    if not keys:
        return 0

    def extend(
        current: tuple[int, int, date],
        key: date,
    ) -> tuple[int, int, date]:
        current_length, longest_length, previous = current
        next_length = current_length + 1 if key == _next_key(previous, period) else 1
        return next_length, max(longest_length, next_length), key

    # The accumulator stores the current run, the best run, and its last key.
    result = reduce(extend, keys[1:], (1, 1, keys[0]))
    return result[1]


def get_longest_streak_all(
    habits: list[Habit],
    checkins_by_habit: dict[int, list[CheckIn]],
) -> tuple[Habit | None, int]:
    """Return the habit with the longest streak and its streak length."""
    longest_habit = habits[0] if habits else None
    longest_streak = 0

    for habit in habits:
        if habit.id is None:
            streak = 0
        else:
            streak = calculate_longest_streak(
                checkins_by_habit.get(habit.id, []),
                habit.period,
            )
        if longest_habit is None or streak > longest_streak:
            longest_habit = habit
            longest_streak = streak

    return longest_habit, longest_streak


def _period_key(completed: date, period: Period) -> date:
    return completed if period is Period.DAILY else completed - timedelta(days=completed.weekday())


def _next_key(previous: date, period: Period) -> date:
    return previous + timedelta(days=1 if period is Period.DAILY else 7)
