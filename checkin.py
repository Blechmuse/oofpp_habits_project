"""Check-in domain model."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class CheckIn:
    """A completion recorded for a habit."""

    id: int | None
    habit_id: int
    completed_at: datetime
