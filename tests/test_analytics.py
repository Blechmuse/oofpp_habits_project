from datetime import datetime, timedelta

from analytics import (
    calculate_longest_streak,
    get_all_habits,
    get_habits_by_period,
    get_longest_streak_all,
)
from checkin import CheckIn
from habit import Habit, Period


BASE = datetime(2026, 1, 5, 9)


def checkins_for_days(days: list[int], habit_id: int = 1) -> list[CheckIn]:
    return [
        CheckIn(None, habit_id, BASE + timedelta(days=day))
        for day in days
    ]


def test_habit_selection_functions_do_not_change_input():
    habits = [
        Habit(1, "Daily", "", Period.DAILY, BASE),
        Habit(2, "Weekly", "", Period.WEEKLY, BASE),
    ]
    original = habits.copy()
    assert get_all_habits(habits) == habits
    assert get_habits_by_period(habits, Period.DAILY) == [habits[0]]
    assert habits == original


def test_daily_streaks_handle_empty_single_gap_duplicates_and_unsorted():
    assert calculate_longest_streak([], Period.DAILY) == 0
    assert calculate_longest_streak(checkins_for_days([0]), Period.DAILY) == 1
    assert calculate_longest_streak(
        checkins_for_days(list(range(28))), Period.DAILY
    ) == 28
    assert calculate_longest_streak(
        checkins_for_days([0, 1, 2, 4]), Period.DAILY
    ) == 3
    assert calculate_longest_streak(
        checkins_for_days([2, 0, 1, 1]), Period.DAILY
    ) == 3


def test_weekly_streaks_normalize_weeks_and_handle_gaps():
    checkins = [
        CheckIn(None, 1, BASE + timedelta(weeks=week))
        for week in [3, 1, 0, 1]
    ]
    assert calculate_longest_streak(checkins, Period.WEEKLY) == 2
    assert calculate_longest_streak(
        [CheckIn(None, 1, BASE + timedelta(weeks=week)) for week in range(4)],
        Period.WEEKLY,
    ) == 4


def test_longest_streak_all_returns_first_tie_and_empty_result():
    assert get_longest_streak_all([], {}) == (None, 0)
    first = Habit(1, "First", "", Period.DAILY, BASE)
    second = Habit(2, "Second", "", Period.DAILY, BASE)
    result = get_longest_streak_all(
        [first, second],
        {1: checkins_for_days([0]), 2: checkins_for_days([4], 2)},
    )
    assert result == (first, 1)


def test_longest_streak_all_uses_each_habits_period():
    daily = Habit(1, "Daily", "", Period.DAILY, BASE)
    weekly = Habit(2, "Weekly", "", Period.WEEKLY, BASE)
    result = get_longest_streak_all(
        [daily, weekly],
        {
            1: checkins_for_days([0, 1, 3]),
            2: [
                CheckIn(None, 2, BASE + timedelta(weeks=week))
                for week in range(4)
            ],
        },
    )
    assert result == (weekly, 4)


def test_expected_seed_streaks(database):
    database.initialize_default_data()
    habits = database.load_habits()
    checkins_by_habit = {
        habit.id: database.load_checkins(habit.id)
        for habit in habits
        if habit.id is not None
    }
    expected = {
        "Morning exercise": 28,
        "Read": 14,
        "Drink water": 4,
        "Meal planning": 4,
        "Weekly review": 2,
    }
    for habit in habits:
        assert calculate_longest_streak(
            checkins_by_habit[habit.id], habit.period
        ) == expected[habit.name]
    assert get_longest_streak_all(habits, checkins_by_habit)[1] == 28
