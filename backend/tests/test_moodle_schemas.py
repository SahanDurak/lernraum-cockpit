from datetime import UTC, datetime

import pytest

from app.moodle.schemas import Assignment, FileContent


@pytest.mark.parametrize("value", [0, None])
def test_zero_timestamps_mean_no_date(value: int | None) -> None:
    file = FileContent.model_validate({"type": "file", "filename": "a.pdf", "timemodified": value})
    assignment = Assignment.model_validate(
        {"id": 1, "cmid": 2, "course": 3, "name": "A", "duedate": value}
    )
    assert file.timemodified is None
    assert assignment.duedate is None


def test_nonzero_timestamps_become_utc_datetimes() -> None:
    stamp = int(datetime(2026, 11, 9, 12, tzinfo=UTC).timestamp())
    file = FileContent.model_validate({"type": "file", "filename": "a.pdf", "timemodified": stamp})
    # Comparing with an aware datetime also proves the result is aware (naive != aware).
    assert file.timemodified == datetime(2026, 11, 9, 12, tzinfo=UTC)
