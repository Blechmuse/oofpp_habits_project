# Habit Tracker

## Project Description

Habit Tracker is a command-line Python application for creating, managing, and
reviewing daily and weekly habits. It stores habits and completions in SQLite
so data remains available between sessions.

## Features

- Create, edit, delete, and complete habits
- Daily and weekly periodicities
- Persistent SQLite storage
- Predefined example data
- Functional analytics
- Longest-streak calculation
- Menu-driven CLI
- pytest test suite

## Technologies

- Python 3.14.7
- SQLite
- pytest
- Visual Studio Code

## Project Structure

- `main.py`: Application entry point and database lifecycle
- `cli.py`: Menu, input handling, and user-facing output
- `habit.py`: Habit model and periodicity enum
- `checkin.py`: Check-in model
- `habitmanager.py`: Habit operations and validation
- `database.py`: SQLite schema and persistence
- `analytics.py`: Pure habit filtering and streak calculations
- `tests/`: Database, manager, analytics, and unit tests

## Requirements

Python 3.14.7 is required for the current development setup. Other Python
3.14 releases should also be compatible.

## Installation

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Running the Application

```text
python main.py
```

## Using the CLI

1. Show all habits
2. Show habits by periodicity
3. Create habit
4. Edit habit
5. Delete habit
6. Complete habit
7. Analytics
8. Exit

Pressing Ctrl+C cancels the application run with a short message.

## Predefined Habits and Example Data

The first start creates these five habits:

- Morning exercise (daily)
- Read (daily)
- Meal planning (weekly)
- Weekly review (weekly)
- Drink water (daily)

Four weeks of example check-ins are created automatically on the first start.
Existing data is never overwritten and the seed data is not duplicated.

## Analytics

The Analytics menu can list all habits, filter habits by periodicity, show the
longest streak of all habits, or show the longest streak of a selected habit.
Daily streaks use consecutive calendar days. Weekly streaks use consecutive
calendar weeks.

## Running the Tests

```text
pytest -v
```

## Database

`habits.db` is created on the first application start. It stores habits and
check-ins between sessions. The test suite uses isolated in-memory databases.

## Known Limitations

- Single-user CLI application
- Only daily and weekly periodicities
- No graphical user interface

## Author

Tobias Aicher
