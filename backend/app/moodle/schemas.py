"""Typed views of Moodle web service responses, plus the interface every Moodle source fulfils.

Only the fields the app uses are modelled; everything else in a response is ignored.
Moodle sends times as Unix timestamps; pydantic turns them into timezone-aware UTC datetimes.
"""

from datetime import datetime
from typing import Protocol

from pydantic import BaseModel, ConfigDict, field_validator


class MoodleModel(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)


class SiteInfo(MoodleModel):
    userid: int
    fullname: str
    release: str = ""


class Course(MoodleModel):
    id: int
    shortname: str
    fullname: str


class FileContent(MoodleModel):
    """One entry of a module's `contents`: usually a file, sometimes a link (`type="url"`)."""

    type: str
    filename: str
    fileurl: str = ""
    filesize: int = 0
    timemodified: datetime | None = None
    mimetype: str = ""


class Module(MoodleModel):
    id: int
    name: str
    modname: str  # e.g. "resource", "folder", "url", "assign", "forum"
    url: str = ""
    contents: list[FileContent] = []


class Section(MoodleModel):
    id: int
    name: str
    section: int  # position within the course, 0 = general section
    modules: list[Module] = []


class Assignment(MoodleModel):
    id: int
    cmid: int  # course module id, used for the link to the assignment page
    course: int
    name: str
    duedate: datetime | None = None

    @field_validator("duedate", mode="before")
    @classmethod
    def _zero_means_no_due_date(cls, value: object) -> object:
        return None if value == 0 else value


class Event(MoodleModel):
    """A calendar event that needs action, e.g. an assignment due date or a quiz closing."""

    id: int
    name: str
    courseid: int | None = None  # None for user or site events
    timestart: datetime
    url: str = ""
    modulename: str = ""


class Announcement(MoodleModel):
    """A discussion in a course's news forum ("Ankündigungen")."""

    id: int  # discussion id
    courseid: int
    subject: str
    message: str  # HTML as sent by Moodle
    author: str
    created: datetime


class MoodleSource(Protocol):
    """What the sync needs from Moodle. Implemented by the real client and the demo client."""

    def site_info(self) -> SiteInfo: ...

    def courses(self, user_id: int) -> list[Course]: ...

    def course_contents(self, course_id: int) -> list[Section]: ...

    def assignments(self, course_ids: list[int]) -> list[Assignment]: ...

    def upcoming_events(self, start: datetime, end: datetime) -> list[Event]: ...

    def announcements(self, course_ids: list[int]) -> list[Announcement]: ...

    def close(self) -> None: ...
