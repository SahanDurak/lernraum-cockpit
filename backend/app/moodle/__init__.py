"""Access to the Lernraum: the real Moodle client or the demo client, chosen by the settings."""

from app.config import Settings
from app.moodle.client import MoodleClient
from app.moodle.demo import DemoMoodleClient
from app.moodle.schemas import MoodleSource


def get_moodle_source(settings: Settings) -> MoodleSource:
    if settings.demo_mode:
        return DemoMoodleClient()
    if not settings.moodle_token.get_secret_value():
        raise RuntimeError("MOODLE_TOKEN is empty. Set it in .env or use DEMO_MODE=true.")
    return MoodleClient(settings.moodle_url, settings.moodle_token)
