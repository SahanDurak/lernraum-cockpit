"""Client for the official Moodle web services (REST, JSON), as used by the Moodle app.

The token is sent in the POST body, never in the URL, so it cannot end up in access or
HTTP client logs. Calls run one after another; the caller keeps the overall rate moderate.
"""

import logging
from datetime import datetime
from typing import Any
from urllib.parse import urlsplit

import httpx2
from pydantic import SecretStr

from app.moodle.schemas import (
    Announcement,
    Assignment,
    Course,
    Event,
    Section,
    SiteInfo,
)

log = logging.getLogger(__name__)

REST_PATH = "/webservice/rest/server.php"
TIMEOUT_SECONDS = 30.0
# Moodle caps action events at 50 per call.
MAX_EVENTS = 50
# Upper bound for paging through events, so a misbehaving server can never cause endless calls.
MAX_EVENT_PAGES = 10
# Newest discussions per news forum; older ones were already seen in earlier syncs.
ANNOUNCEMENTS_PER_FORUM = 20


class MoodleError(Exception):
    """A call failed: Moodle error object (e.g. `invalidtoken`), HTTP status or network error."""

    def __init__(self, function: str, errorcode: str, message: str) -> None:
        super().__init__(f"{function}: {errorcode} – {message}")
        self.errorcode = errorcode


def _encode(params: dict[str, Any]) -> dict[str, str]:
    """Flatten lists into Moodle's array syntax: {"ids": [1, 2]} -> {"ids[0]": "1", ...}."""
    flat: dict[str, str] = {}
    for key, value in params.items():
        if isinstance(value, list):
            for index, item in enumerate(value):
                flat[f"{key}[{index}]"] = str(item)
        else:
            flat[key] = str(value)
    return flat


class MoodleClient:
    def __init__(self, base_url: str, token: SecretStr, http: httpx2.Client | None = None) -> None:
        parts = urlsplit(base_url)
        if parts.scheme != "https" or not parts.hostname:
            # The token is sent with every request; never over plain HTTP.
            raise ValueError("Moodle base URL must be an https:// URL")
        self._url = base_url.rstrip("/") + REST_PATH
        self._token = token
        self._http = http or httpx2.Client(timeout=TIMEOUT_SECONDS)

    def __repr__(self) -> str:
        return f"MoodleClient({self._url!r})"

    def close(self) -> None:
        self._http.close()

    def _call(self, function: str, **params: Any) -> Any:
        data = _encode(params) | {
            "wstoken": self._token.get_secret_value(),
            "wsfunction": function,
            "moodlewsrestformat": "json",
        }
        try:
            response = self._http.post(self._url, data=data)
            response.raise_for_status()
        except httpx2.HTTPStatusError as error:
            # Re-raised without the original: its request object carries the token in the body.
            status = error.response.status_code
            raise MoodleError(function, "http", f"HTTP {status}") from None
        except httpx2.HTTPError as error:
            raise MoodleError(function, "network", type(error).__name__) from None
        result = response.json()
        if isinstance(result, dict) and "exception" in result:
            raise MoodleError(function, result.get("errorcode", ""), result.get("message", ""))
        return result

    def site_info(self) -> SiteInfo:
        return SiteInfo.model_validate(self._call("core_webservice_get_site_info"))

    def courses(self, user_id: int) -> list[Course]:
        result = self._call("core_enrol_get_users_courses", userid=user_id)
        return [Course.model_validate(course) for course in result]

    def course_contents(self, course_id: int) -> list[Section]:
        result = self._call("core_course_get_contents", courseid=course_id)
        return [Section.model_validate(section) for section in result]

    def assignments(self, course_ids: list[int]) -> list[Assignment]:
        if not course_ids:
            return []
        result = self._call("mod_assign_get_assignments", courseids=course_ids)
        return [
            Assignment.model_validate(assignment)
            for course in result.get("courses", [])
            for assignment in course.get("assignments", [])
        ]

    def upcoming_events(self, start: datetime, end: datetime) -> list[Event]:
        if start.tzinfo is None or end.tzinfo is None:
            raise ValueError("start and end must be timezone-aware")
        params: dict[str, Any] = {
            "timesortfrom": int(start.timestamp()),
            "timesortto": int(end.timestamp()),
            "limitnum": MAX_EVENTS,
        }
        events: list[Event] = []
        for _ in range(MAX_EVENT_PAGES):
            page = self._call("core_calendar_get_action_events_by_timesort", **params)
            raw_events = page.get("events", [])
            events.extend(
                Event.model_validate(event | {"courseid": (event.get("course") or {}).get("id")})
                for event in raw_events
            )
            if len(raw_events) < MAX_EVENTS or events[-1].id == params.get("aftereventid"):
                return events
            # A full page: there may be more, continue after the last one.
            params["aftereventid"] = events[-1].id
        log.warning("Stopped paging calendar events after %d pages", MAX_EVENT_PAGES)
        return events

    def announcements(self, course_ids: list[int]) -> list[Announcement]:
        if not course_ids:
            return []
        forums = self._call("mod_forum_get_forums_by_courses", courseids=course_ids)
        announcements: list[Announcement] = []
        for forum in forums:
            if forum.get("type") != "news":
                continue
            result = self._call(
                "mod_forum_get_forum_discussions",
                forumid=forum["id"],
                page=0,
                perpage=ANNOUNCEMENTS_PER_FORUM,
            )
            # model_validate (not the constructor): a missing field raises a ValidationError
            # that names the field, instead of a bare KeyError.
            announcements.extend(
                Announcement.model_validate(
                    {
                        "id": discussion.get("discussion"),
                        "courseid": forum.get("course"),
                        "subject": discussion.get("subject"),
                        "message": discussion.get("message"),
                        "author": discussion.get("userfullname", ""),
                        "created": discussion.get("created"),
                    }
                )
                for discussion in result.get("discussions", [])
            )
        return announcements
