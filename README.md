# Habit Tracker

A Python 3.12 command-line habit tracker using SQLite.

## Run

```text
python main.py
```

The first run creates `habits.db`, five predefined habits, and four weeks of example check-ins.

## Test

```text
python -m pytest
```

Core dependencies follow the required architecture: `CLI -> HabitManager`, `CLI -> analytics functions`, `HabitManager -> Habit/SQLite Database`, and analytics functions query SQLite through `Database`.
