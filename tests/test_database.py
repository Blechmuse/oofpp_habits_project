from datetime import datetime, timedelta

from checkin import CheckIn
from habit import Habit, Period


def make_habit(name: str = "Exercise", period: Period = Period.DAILY) -> Habit:
    return Habit(None, name, "Description", period, datetime(2026, 1, 1, 9))


def test_tables_are_created(database):
    tables = {
        row["name"]
        for row in database.connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
    }
    assert {"habits", "checkins"} <= tables


def test_habit_is_saved_and_reconstructed(database):
    habit = database.insert_habit(make_habit("Read", Period.WEEKLY))
    loaded = database.load_habit(habit.id)
    assert loaded == habit
    assert loaded.period is Period.WEEKLY


def test_daily_and_weekly_periods_are_persisted(database):
    daily = database.insert_habit(make_habit("Daily", Period.DAILY))
    weekly = database.insert_habit(make_habit("Weekly", Period.WEEKLY))
    assert database.load_habit(daily.id).period is Period.DAILY
    assert database.load_habit(weekly.id).period is Period.WEEKLY


def test_checkins_can_be_saved_and_loaded(database):
    habit = database.insert_habit(make_habit())
    checkin = database.insert_checkin(
        CheckIn(None, habit.id, datetime(2026, 1, 2, 9))
    )
    assert database.load_checkins(habit.id) == [checkin]


def test_load_checkins_can_filter_by_habit(database):
    first = database.insert_habit(make_habit("First"))
    second = database.insert_habit(make_habit("Second"))
    first_checkin = database.insert_checkin(
        CheckIn(None, first.id, datetime(2026, 1, 2, 9))
    )
    second_checkin = database.insert_checkin(
        CheckIn(None, second.id, datetime(2026, 1, 3, 9))
    )
    assert database.load_checkins(first.id) == [first_checkin]
    assert database.load_checkins() == [first_checkin, second_checkin]


def test_deleting_habit_cascades_to_checkins(database):
    habit = database.insert_habit(make_habit())
    database.insert_checkin(CheckIn(None, habit.id, datetime.now()))
    database.delete_habit(habit.id)
    assert database.load_habit(habit.id) is None
    assert database.load_checkins(habit.id) == []


def test_default_data_has_expected_habits_and_streak_window(database):
    database.initialize_default_data()
    habits = database.load_habits()
    assert len(habits) == 5
    assert {habit.period for habit in habits} == {Period.DAILY, Period.WEEKLY}
    assert all(database.load_checkins(habit.id) for habit in habits)
    assert all(
        checkin.completed_at >= habits[0].created_at - timedelta(days=27)
        for habit in habits
        for checkin in database.load_checkins(habit.id)
    )


def test_default_data_is_not_duplicated(database):
    database.initialize_default_data()
    first_counts = len(database.load_checkins())
    database.initialize_default_data()
    assert len(database.load_habits()) == 5
    assert len(database.load_checkins()) == first_counts
