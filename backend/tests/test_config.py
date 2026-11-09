import pytest
from pydantic import ValidationError

from app.config import Settings


def test_sync_interval_is_read_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SYNC_INTERVAL_MINUTES", "15")
    # _env_file=None: tests never read the developer's real settings file.
    assert Settings(_env_file=None).sync_interval_minutes == 15  # pyright: ignore[reportCallIssue]


def test_sync_interval_defaults_to_60(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SYNC_INTERVAL_MINUTES", raising=False)
    assert Settings(_env_file=None).sync_interval_minutes == 60  # pyright: ignore[reportCallIssue]


def test_sync_interval_must_be_positive(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SYNC_INTERVAL_MINUTES", "0")
    with pytest.raises(ValidationError):
        Settings(_env_file=None)  # pyright: ignore[reportCallIssue]
