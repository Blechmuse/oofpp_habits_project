"""Unit tests for the habit tracker."""

from datetime import datetime, timedelta

from analytics import calculate_longest_streak, get_habits_by_period
from checkin import CheckIn
from database import Database
from habit import Period
from habitmanager import HabitManager


def make_manager(tmp_path):
    database = Database(tmp_path / "test.db")
    return database, HabitManager(database)


def test_habit_creation(tmp_path):
    database, manager = make_manager(tmp_path)
    habit = manager.create_habit("Exercise", "Run", Period.DAILY)
    assert habit.id is not None
    assert manager.get_habit(habit.id).name == "Exercise"
    database.close()


def test_habit_completion(tmp_path):
    database, manager = make_manager(tmp_path)
    habit = manager.create_habit("Read", "Book", Period.DAILY)
    checkin = manager.complete_habit(habit.id)
    assert checkin.habit_id == habit.id
    assert len(database.load_checkins(habit.id)) == 1
    database.close()


def test_database_persistence(tmp_path):
    path = tmp_path / "persistent.db"
    first = Database(path)
    habit = HabitManager(first).create_habit("Meditate", "", Period.DAILY)
    first.close()
    second = Database(path)
    assert second.load_habit(habit.id).name == "Meditate"
    second.close()


def test_longest_streak_calculation(tmp_path):
    database, manager = make_manager(tmp_path)
    habit = manager.create_habit("Walk", "", Period.DAILY)
    start = datetime(2026, 1, 1)
    for offset in (0, 1, 2, 4):
        database.insert_checkin(CheckIn(None, habit.id, start + timedelta(days=offset)))
    assert calculate_longest_streak(
        database.load_checkins(habit.id), Period.DAILY
    ) == 3
    database.close()


def test_filtering_by_periodicity(tmp_path):
    database, manager = make_manager(tmp_path)
    manager.create_habit("Daily", "", Period.DAILY)
    manager.create_habit("Weekly", "", Period.WEEKLY)
    assert [
        habit.name
        for habit in get_habits_by_period(database.load_habits(), Period.WEEKLY)
    ] == ["Weekly"]
    database.close()
