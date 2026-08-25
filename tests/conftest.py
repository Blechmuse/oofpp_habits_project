from collections.abc import Iterator

import pytest

from database import Database


@pytest.fixture
def database() -> Iterator[Database]:
    database = Database(":memory:")
    yield database
    database.close()
