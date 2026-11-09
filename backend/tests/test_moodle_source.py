import pytest
from pydantic import SecretStr

from app.config import Settings
from app.moodle import get_moodle_source
from app.moodle.client import MoodleClient
from app.moodle.demo import DemoMoodleClient


def make_settings(**values: object) -> Settings:
    # _env_file=None: tests never read the developer's real settings file.
    return Settings(_env_file=None, **values)  # pyright: ignore[reportCallIssue]


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("DEMO_MODE", "MOODLE_URL", "MOODLE_TOKEN"):
        monkeypatch.delenv(name, raising=False)


def test_demo_mode_returns_demo_client_even_without_token() -> None:
    source = get_moodle_source(make_settings(demo_mode=True))
    assert isinstance(source, DemoMoodleClient)


def test_empty_token_raises() -> None:
    with pytest.raises(RuntimeError, match="MOODLE_TOKEN"):
        get_moodle_source(make_settings(moodle_token=SecretStr("")))


def test_plain_http_url_raises() -> None:
    settings = make_settings(
        moodle_url="http://moodle.example.invalid", moodle_token=SecretStr("test-token")
    )
    with pytest.raises(ValueError, match="https"):
        get_moodle_source(settings)


def test_otherwise_real_client() -> None:
    settings = make_settings(
        moodle_url="https://moodle.example.invalid", moodle_token=SecretStr("test-token")
    )
    source = get_moodle_source(settings)
    try:
        assert isinstance(source, MoodleClient)
        assert "test-token" not in repr(source)
    finally:
        source.close()
