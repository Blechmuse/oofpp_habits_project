import pytest

from habit import Period
from habitmanager import HabitManager


def test_create_habit_strips_fields(database):
    manager = HabitManager(database)
    habit = manager.create_habit("  Exercise  ", "  Run  ", Period.DAILY)
    assert habit.name == "Exercise"
    assert habit.description == "Run"


@pytest.mark.parametrize("name", ["", "   "])
def test_empty_name_is_rejected(database, name):
    with pytest.raises(ValueError, match="cannot be empty"):
        HabitManager(database).create_habit(name, "", Period.DAILY)


def test_update_existing_habit(database):
    manager = HabitManager(database)
    habit = manager.create_habit("Old", "Description", Period.DAILY)
    updated = manager.update_habit(habit.id, " New ", " Updated ", Period.WEEKLY)
    assert updated.name == "New"
    assert updated.description == "Updated"
    assert updated.period is Period.WEEKLY


def test_update_missing_habit_is_rejected(database):
    with pytest.raises(ValueError, match="not found"):
        HabitManager(database).update_habit(999, "Name", "", Period.DAILY)


def test_delete_existing_habit(database):
    manager = HabitManager(database)
    habit = manager.create_habit("Delete me", "", Period.DAILY)
    manager.delete_habit(habit.id)
    assert manager.get_habit(habit.id) is None


def test_delete_missing_habit_is_rejected(database):
    with pytest.raises(ValueError, match="not found"):
        HabitManager(database).delete_habit(999)


def test_complete_existing_habit_creates_checkin(database):
    manager = HabitManager(database)
    habit = manager.create_habit("Read", "", Period.DAILY)
    checkin = manager.complete_habit(habit.id)
    assert checkin.habit_id == habit.id
    assert len(database.load_checkins(habit.id)) == 1


def test_complete_missing_habit_is_rejected(database):
    with pytest.raises(ValueError, match="not found"):
        HabitManager(database).complete_habit(999)


def test_list_and_get_habits(database):
    manager = HabitManager(database)
    first = manager.create_habit("First", "", Period.DAILY)
    second = manager.create_habit("Second", "", Period.WEEKLY)
    assert manager.list_habits() == [first, second]
    assert manager.get_habit(first.id) == first
    assert manager.get_habit(999) is None
