from collections.abc import Iterator
from datetime import timedelta

import pytest

from analytics import calculate_longest_streak
from database import Database
from habit import Period


@pytest.fixture
def default_database(tmp_path) -> Iterator[Database]:
    database = Database(tmp_path / "default_data.db")
    database.initialize_default_data()
    yield database
    database.close()


def habits_by_name(database: Database):
    return {habit.name: habit for habit in database.load_habits()}


def period_keys(database: Database, habit_id: int, period: Period):
    checkins = database.load_checkins(habit_id)
    dates = [checkin.completed_at.date() for checkin in checkins]
    if period is Period.WEEKLY:
        dates = [date - timedelta(days=date.weekday()) for date in dates]
    return sorted(set(dates))


def test_initialize_default_data_creates_exactly_five_habits(default_database):
    assert len(default_database.load_habits()) == 5


def test_default_data_contains_daily_and_weekly_habits(default_database):
    periods = {habit.period for habit in default_database.load_habits()}

    assert Period.DAILY in periods
    assert Period.WEEKLY in periods


def test_every_default_habit_has_checkins(default_database):
    for habit in default_database.load_habits():
        assert habit.id is not None
        assert default_database.load_checkins(habit.id)


def test_default_checkins_are_not_before_habit_creation(default_database):
    for habit in default_database.load_habits():
        assert habit.id is not None
        assert all(
            checkin.completed_at >= habit.created_at
            for checkin in default_database.load_checkins(habit.id)
        )


def test_default_checkins_cover_four_week_test_period(default_database):
    for habit in default_database.load_habits():
        assert habit.id is not None
        keys = period_keys(default_database, habit.id, habit.period)

        expected_span = timedelta(days=27 if habit.period is Period.DAILY else 21)
        assert keys[-1] - keys[0] == expected_span


def test_morning_exercise_has_a_28_day_streak(default_database):
    habit = habits_by_name(default_database)["Morning exercise"]

    assert habit.id is not None
    assert calculate_longest_streak(
        default_database.load_checkins(habit.id),
        habit.period,
    ) == 28


def test_meal_planning_has_a_four_week_streak(default_database):
    habit = habits_by_name(default_database)["Meal planning"]

    assert habit.id is not None
    assert calculate_longest_streak(
        default_database.load_checkins(habit.id),
        habit.period,
    ) == 4


def test_weekly_review_has_a_two_week_streak(default_database):
    habit = habits_by_name(default_database)["Weekly review"]

    assert habit.id is not None
    assert calculate_longest_streak(
        default_database.load_checkins(habit.id),
        habit.period,
    ) == 2


def test_default_data_is_not_duplicated(default_database):
    first_habit_count = len(default_database.load_habits())
    first_checkin_count = len(default_database.load_checkins())

    default_database.initialize_default_data()

    assert len(default_database.load_habits()) == first_habit_count
    assert len(default_database.load_checkins()) == first_checkin_count


def test_deleting_default_habit_cascades_to_checkins(default_database):
    habit = habits_by_name(default_database)["Morning exercise"]
    assert habit.id is not None
    assert default_database.load_checkins(habit.id)

    default_database.delete_habit(habit.id)

    assert default_database.load_habit(habit.id) is None
    assert default_database.load_checkins(habit.id) == []
