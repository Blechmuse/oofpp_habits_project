"""Entry point for the habit tracker."""

from cli import CLI
from database import Database
from habitmanager import HabitManager


def main() -> None:
    """Initialize persistence and start the menu-driven CLI."""
    database = Database()
    try:
        database.initialize_default_data()
        CLI(HabitManager(database), database).run()
    finally:
        database.close()


if __name__ == "__main__":
    main()
