"""Habit domain model."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Period(Enum):
    """Supported habit frequencies."""

    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass
class Habit:
    """A habit tracked by the application."""

    id: int | None
    name: str
    description: str
    period: Period
    created_at: datetime
