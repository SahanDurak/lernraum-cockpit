"""Tests for the real Moodle client. No network: every response comes from a MockTransport.

All sample data is invented; the token is a dummy value.
"""

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any
from urllib.parse import parse_qs

import httpx2
import pytest
from pydantic import SecretStr, ValidationError

from app.moodle.client import MoodleClient, MoodleError

BASE_URL = "https://moodle.example.invalid"
TOKEN = "test-token"
REST_URL = f"{BASE_URL}/webservice/rest/server.php"

Handler = Callable[[str, dict[str, str]], Any]


class Recorder:
    """Answers each request via `handler(wsfunction, form)` and remembers what was sent."""

    def __init__(self, handler: Handler) -> None:
        self.handler = handler
        self.requests: list[httpx2.Request] = []
        self.forms: list[dict[str, str]] = []

    def __call__(self, request: httpx2.Request) -> httpx2.Response:
        self.requests.append(request)
        form = {key: values[0] for key, values in parse_qs(request.content.decode()).items()}
        self.forms.append(form)
        return httpx2.Response(200, json=self.handler(form["wsfunction"], form))


def make_client(handler: Handler, base_url: str = BASE_URL) -> tuple[MoodleClient, Recorder]:
    recorder = Recorder(handler)
    http = httpx2.Client(transport=httpx2.MockTransport(recorder))
    return MoodleClient(base_url, SecretStr(TOKEN), http=http), recorder


def ts(year: int, month: int, day: int, hour: int = 0) -> int:
    return int(datetime(year, month, day, hour, tzinfo=UTC).timestamp())


# --- request format ------------------------------------------------------------------------


@pytest.mark.parametrize("base_url", [BASE_URL, BASE_URL + "/"])
def test_request_is_post_with_token_in_body(base_url: str) -> None:
    client, recorder = make_client(lambda *_: {"userid": 7, "fullname": "Test Person"}, base_url)
    client.site_info()

    request = recorder.requests[0]
    assert request.method == "POST"
    assert str(request.url) == REST_URL
    assert TOKEN not in str(request.url)
    assert recorder.forms[0] == {
        "wstoken": TOKEN,
        "wsfunction": "core_webservice_get_site_info",
        "moodlewsrestformat": "json",
    }


def test_list_params_use_moodle_array_syntax() -> None:
    client, recorder = make_client(lambda *_: {"courses": []})
    client.assignments([11, 22])

    form = recorder.forms[0]
    assert form["courseids[0]"] == "11"
    assert form["courseids[1]"] == "22"
    assert "courseids" not in form


# --- parsing -------------------------------------------------------------------------------


def test_site_info() -> None:
    client, _ = make_client(
        lambda *_: {
            "sitename": "Demo Moodle",
            "userid": 42,
            "fullname": "Erika Beispiel",
            "release": "4.5.1 (Build: 20250101)",
        }
    )
    info = client.site_info()
    assert info.userid == 42
    assert info.fullname == "Erika Beispiel"
    assert info.release.startswith("4.5")


def test_courses() -> None:
    client, recorder = make_client(
        lambda *_: [
            {"id": 3, "shortname": "PHY", "fullname": "Physik 1", "visible": 1},
            {"id": 4, "shortname": "INF", "fullname": "Informatik 1", "visible": 1},
        ]
    )
    courses = client.courses(42)
    assert recorder.forms[0]["wsfunction"] == "core_enrol_get_users_courses"
    assert recorder.forms[0]["userid"] == "42"
    assert [(c.id, c.shortname, c.fullname) for c in courses] == [
        (3, "PHY", "Physik 1"),
        (4, "INF", "Informatik 1"),
    ]


def test_course_contents_with_files() -> None:
    modified = ts(2026, 10, 1, 12)
    client, recorder = make_client(
        lambda *_: [
            {
                "id": 30,
                "name": "Allgemeines",
                "section": 0,
                "visible": 1,
                "modules": [
                    {
                        "id": 301,
                        "name": "Skript Kapitel 1",
                        "modname": "resource",
                        "url": f"{BASE_URL}/mod/resource/view.php?id=301",
                        "contents": [
                            {
                                "type": "file",
                                "filename": "Kapitel_1.pdf",
                                "fileurl": f"{BASE_URL}/webservice/pluginfile.php/1/Kapitel_1.pdf",
                                "filesize": 123456,
                                "timemodified": modified,
                                "mimetype": "application/pdf",
                                "author": "Jemand",
                            }
                        ],
                    },
                    {"id": 302, "name": "Ankündigungen", "modname": "forum"},
                ],
            },
            {"id": 31, "name": "Woche 1", "section": 1},
        ]
    )
    sections = client.course_contents(3)

    assert recorder.forms[0]["wsfunction"] == "core_course_get_contents"
    assert recorder.forms[0]["courseid"] == "3"
    assert [s.name for s in sections] == ["Allgemeines", "Woche 1"]
    assert sections[1].modules == []

    resource, forum = sections[0].modules
    assert forum.contents == []
    file = resource.contents[0]
    assert file.filename == "Kapitel_1.pdf"
    assert file.filesize == 123456
    assert file.mimetype == "application/pdf"
    assert file.timemodified == datetime(2026, 10, 1, 12, tzinfo=UTC)
    assert file.timemodified is not None and file.timemodified.tzinfo is not None


def test_assignments_nested_in_courses_and_zero_duedate_is_none() -> None:
    client, recorder = make_client(
        lambda *_: {
            "courses": [
                {
                    "id": 3,
                    "assignments": [
                        {"id": 1, "cmid": 91, "course": 3, "name": "Blatt 1", "duedate": 0},
                        {
                            "id": 2,
                            "cmid": 92,
                            "course": 3,
                            "name": "Blatt 2",
                            "duedate": ts(2026, 11, 20, 23),
                        },
                    ],
                },
                {
                    "id": 4,
                    "assignments": [
                        {
                            "id": 3,
                            "cmid": 93,
                            "course": 4,
                            "name": "Projekt",
                            "duedate": ts(2026, 12, 1),
                        }
                    ],
                },
            ],
            "warnings": [],
        }
    )
    assignments = client.assignments([3, 4])

    assert recorder.forms[0]["wsfunction"] == "mod_assign_get_assignments"
    assert [(a.id, a.cmid, a.course, a.name) for a in assignments] == [
        (1, 91, 3, "Blatt 1"),
        (2, 92, 3, "Blatt 2"),
        (3, 93, 4, "Projekt"),
    ]
    assert assignments[0].duedate is None
    assert assignments[1].duedate == datetime(2026, 11, 20, 23, tzinfo=UTC)


def test_upcoming_events() -> None:
    start = datetime(2026, 11, 9, tzinfo=UTC)
    end = datetime(2026, 11, 30, tzinfo=UTC)
    client, recorder = make_client(
        lambda *_: {
            "events": [
                {
                    "id": 801,
                    "name": "Blatt 2 ist fällig",
                    "course": {"id": 3, "fullname": "Physik 1"},
                    "timestart": ts(2026, 11, 20, 23),
                    "url": f"{BASE_URL}/mod/assign/view.php?id=92",
                    "modulename": "assign",
                },
                {"id": 802, "name": "Eigener Termin", "timestart": ts(2026, 11, 21)},
            ],
            "firstid": 801,
            "lastid": 802,
        }
    )
    events = client.upcoming_events(start, end)

    form = recorder.forms[0]
    assert form["wsfunction"] == "core_calendar_get_action_events_by_timesort"
    assert form["timesortfrom"] == str(int(start.timestamp()))
    assert form["timesortto"] == str(int(end.timestamp()))
    assert form["limitnum"].isdigit() and int(form["limitnum"]) > 0

    assert events[0].courseid == 3
    assert events[0].timestart == datetime(2026, 11, 20, 23, tzinfo=UTC)
    assert events[0].modulename == "assign"
    assert events[1].courseid is None


def test_upcoming_events_pages_through_full_results() -> None:
    def event(event_id: int) -> dict[str, Any]:
        return {"id": event_id, "name": f"E{event_id}", "timestart": ts(2026, 12, 1)}

    def handler(_: str, form: dict[str, str]) -> Any:
        if "aftereventid" not in form:
            return {"events": [event(i) for i in range(1, 51)]}  # a full page of 50
        return {"events": [event(51)]}

    client, recorder = make_client(handler)
    start = datetime(2026, 11, 9, tzinfo=UTC)
    events = client.upcoming_events(start, datetime(2026, 12, 9, tzinfo=UTC))

    assert [e.id for e in events] == list(range(1, 52))
    assert len(recorder.forms) == 2
    assert recorder.forms[1]["aftereventid"] == "50"


def test_upcoming_events_rejects_naive_datetimes() -> None:
    client, recorder = make_client(lambda *_: {"events": []})
    with pytest.raises(ValueError):
        client.upcoming_events(datetime(2026, 11, 9), datetime(2026, 12, 9, tzinfo=UTC))
    assert recorder.requests == []


def test_announcements_only_from_news_forums() -> None:
    def handler(function: str, form: dict[str, str]) -> Any:
        if function == "mod_forum_get_forums_by_courses":
            return [
                {"id": 61, "course": 3, "type": "news", "name": "Ankündigungen"},
                {"id": 62, "course": 3, "type": "general", "name": "Diskussionsforum"},
                {"id": 63, "course": 4, "type": "news", "name": "Ankündigungen"},
            ]
        assert function == "mod_forum_get_forum_discussions"
        if form["forumid"] == "61":
            return {
                "discussions": [
                    {
                        "id": 9001,  # post id, not the discussion id
                        "discussion": 501,
                        "subject": "Klausurtermin",
                        "message": "<p>Die Klausur ist am 1. Februar.</p>",
                        "userfullname": "Prof. Beispiel",
                        "created": ts(2026, 11, 2, 9),
                    }
                ]
            }
        return {"discussions": []}

    client, recorder = make_client(handler)
    announcements = client.announcements([3, 4])

    discussion_calls = [
        form for form in recorder.forms if form["wsfunction"] == "mod_forum_get_forum_discussions"
    ]
    assert sorted(form["forumid"] for form in discussion_calls) == ["61", "63"]

    assert len(announcements) == 1
    announcement = announcements[0]
    assert announcement.id == 501
    assert announcement.courseid == 3
    assert announcement.subject == "Klausurtermin"
    assert announcement.message == "<p>Die Klausur ist am 1. Februar.</p>"
    assert announcement.author == "Prof. Beispiel"
    assert announcement.created == datetime(2026, 11, 2, 9, tzinfo=UTC)


@pytest.mark.parametrize("method", ["assignments", "announcements"])
def test_empty_course_ids_make_no_request(method: str) -> None:
    client, recorder = make_client(lambda *_: pytest.fail("no request expected"))
    assert getattr(client, method)([]) == []
    assert recorder.requests == []


# --- errors --------------------------------------------------------------------------------


def test_moodle_error_object_raises_without_leaking_token() -> None:
    client, _ = make_client(
        lambda *_: {
            "exception": "moodle_exception",
            "errorcode": "invalidtoken",
            "message": "Ungültiges Token - Token wurde nicht gefunden",
        }
    )
    with pytest.raises(MoodleError) as excinfo:
        client.site_info()

    assert excinfo.value.errorcode == "invalidtoken"
    assert TOKEN not in str(excinfo.value)
    assert TOKEN not in repr(excinfo.value)
    assert TOKEN not in repr(client)


def test_http_error_raises_moodle_error_without_request() -> None:
    http = httpx2.Client(transport=httpx2.MockTransport(lambda _: httpx2.Response(500)))
    client = MoodleClient(BASE_URL, SecretStr(TOKEN), http=http)
    with pytest.raises(MoodleError) as excinfo:
        client.site_info()
    assert excinfo.value.errorcode == "http"
    assert TOKEN not in str(excinfo.value)
    # The httpx2 error (whose request body holds the token) is not shown as the cause.
    assert excinfo.value.__cause__ is None
    assert excinfo.value.__suppress_context__


def test_non_json_response_raises_moodle_error() -> None:
    page = httpx2.Response(200, text="<html>Wartungsmodus</html>")
    http = httpx2.Client(transport=httpx2.MockTransport(lambda _: page))
    client = MoodleClient(BASE_URL, SecretStr(TOKEN), http=http)
    with pytest.raises(MoodleError) as excinfo:
        client.site_info()
    assert excinfo.value.errorcode == "invalid_response"
    assert "Wartungsmodus" not in str(excinfo.value)


def test_network_error_raises_moodle_error() -> None:
    def fail(request: httpx2.Request) -> httpx2.Response:
        raise httpx2.ConnectError("unreachable", request=request)

    client = MoodleClient(
        BASE_URL, SecretStr(TOKEN), http=httpx2.Client(transport=httpx2.MockTransport(fail))
    )
    with pytest.raises(MoodleError) as excinfo:
        client.site_info()
    assert excinfo.value.errorcode == "network"


@pytest.mark.parametrize(
    "base_url", ["http://moodle.example.invalid", "moodle.example.invalid", "https://"]
)
def test_constructor_requires_https_url(base_url: str) -> None:
    with pytest.raises(ValueError, match="https"):
        MoodleClient(base_url, SecretStr(TOKEN))


def test_upcoming_events_stops_when_server_repeats_full_page() -> None:
    page = {
        "events": [{"id": i, "name": f"E{i}", "timestart": ts(2026, 12, 1)} for i in range(1, 51)]
    }
    client, recorder = make_client(lambda *_: page)
    client.upcoming_events(datetime(2026, 11, 9, tzinfo=UTC), datetime(2026, 12, 9, tzinfo=UTC))
    assert len(recorder.forms) == 2  # second page is identical -> stop


def test_upcoming_events_page_limit() -> None:
    calls = 0

    def handler(*_: Any) -> Any:
        nonlocal calls
        calls += 1
        first = calls * 100
        return {
            "events": [
                {"id": first + i, "name": "E", "timestart": ts(2026, 12, 1)} for i in range(50)
            ]
        }

    client, recorder = make_client(handler)
    client.upcoming_events(datetime(2026, 11, 9, tzinfo=UTC), datetime(2026, 12, 9, tzinfo=UTC))
    assert len(recorder.forms) == 10


def test_incomplete_discussion_raises_validation_error() -> None:
    def handler(function: str, _: dict[str, str]) -> Any:
        if function == "mod_forum_get_forums_by_courses":
            return [{"id": 1, "course": 3, "type": "news"}]
        return {"discussions": [{"discussion": 9, "message": "<p>x</p>", "created": 0}]}

    client, _ = make_client(handler)
    with pytest.raises(ValidationError, match="subject"):
        client.announcements([3])
