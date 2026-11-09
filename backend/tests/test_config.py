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


def test_moodle_settings_are_read_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEMO_MODE", "true")
    monkeypatch.setenv("MOODLE_URL", "https://moodle.example.invalid")
    monkeypatch.setenv("MOODLE_TOKEN", "test-token")
    settings = Settings(_env_file=None)  # pyright: ignore[reportCallIssue]
    assert settings.demo_mode is True
    assert settings.moodle_url == "https://moodle.example.invalid"
    assert settings.moodle_token.get_secret_value() == "test-token"


def test_moodle_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("DEMO_MODE", "MOODLE_URL", "MOODLE_TOKEN"):
        monkeypatch.delenv(name, raising=False)
    settings = Settings(_env_file=None)  # pyright: ignore[reportCallIssue]
    assert settings.demo_mode is False
    assert settings.moodle_url.startswith("https://")
    assert settings.moodle_token.get_secret_value() == ""


def test_token_is_not_in_repr(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MOODLE_TOKEN", "test-token")
    settings = Settings(_env_file=None)  # pyright: ignore[reportCallIssue]
    assert "test-token" not in repr(settings)
    assert "test-token" not in str(settings)
