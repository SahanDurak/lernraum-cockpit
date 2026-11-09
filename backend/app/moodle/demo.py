"""Demo source with invented sample data: no network, no token, no real Lernraum data.

Used for demo mode (screenshots, trying the app) and tests. Due dates and posting times are
relative to `now`, so the dashboard always has upcoming deadlines and recent news.
All names, files and texts are made up.
"""

from datetime import UTC, datetime, timedelta

from app.moodle.schemas import (
    Announcement,
    Assignment,
    Course,
    Event,
    FileContent,
    Module,
    Section,
    SiteInfo,
)

DEMO_USER_ID = 1
# .invalid is reserved and never resolves, so demo links can never reach a real server.
DEMO_BASE_URL = "https://lernraum.demo.invalid"

# course id -> (shortname, fullname, {section name: [file names]})
_COURSES: dict[int, tuple[str, str, dict[str, list[str]]]] = {
    101: (
        "MA1",
        "Mathematik 1",
        {
            "Allgemeines": ["Modulhandbuch_Mathematik_1.pdf"],
            "Folgen und Reihen": ["MA1_Folgen_und_Reihen.pdf", "MA1_Uebung_1.pdf"],
            "Differentialrechnung": ["MA1_Kapitel_2_Ableitungen.pdf", "MA1_Uebung_2.pdf"],
        },
    ),
    102: (
        "BWL",
        "Grundlagen BWL",
        {
            "Allgemeines": ["BWL_Organisatorisches.pdf"],
            "Unternehmensziele": ["BWL_VL_01_Ziele.pdf"],
            "Kosten- und Leistungsrechnung": ["BWL_VL_02_KLR.pdf", "BWL_Fallstudie_KLR.xlsx"],
        },
    ),
    103: (
        "TM",
        "Technische Mechanik",
        {
            "Statik": ["TM_Kapitel_1_Kraefte.pdf", "TM_Uebung_Gleichgewicht.pdf"],
            "Festigkeitslehre": ["TM_Kapitel_2_Spannungen.pdf"],
        },
    ),
    104: (
        "PM",
        "Projektmanagement",
        {
            "Grundlagen": ["PM_VL_01_Projektbegriff.pdf"],
            "Planung": ["PM_VL_02_Netzplantechnik.pdf", "PM_Vorlage_Projektauftrag.docx"],
        },
    ),
    105: (
        "ACS",
        "Regelungstechnik (ACS)",
        {
            "Allgemeines": ["RT_Formelsammlung.pdf"],
            "Laplace-Transformation": [
                "RT_Kapitel_3_Laplace-Transformation.pdf",
                "RT_Korrespondenztabelle_Laplace.pdf",
                "RT_Uebung_3_Ruecktransformation_Partialbruchzerlegung.pdf",
            ],
            "Übertragungsfunktionen": [
                "RT_Kapitel_4_Uebertragungsfunktion_und_Pol-Nullstellen.pdf",
                "RT_Uebung_4_Sprungantwort_PT1_PT2.pdf",
            ],
        },
    ),
}

# (id, course id, name, due in days relative to now; negative = already past)
_ASSIGNMENTS: list[tuple[int, int, str, int]] = [
    (501, 101, "Hausaufgabe 2: Ableitungen", 2),
    (502, 105, "Übung 3: Laplace-Rücktransformation", 5),
    (503, 104, "Projektauftrag abgeben", 12),
    (504, 102, "Fallstudie Kostenrechnung", -3),
]

# (id, course id, subject, message, author, posted days ago)
_ANNOUNCEMENTS: list[tuple[int, int, str, str, str, int]] = [
    (
        701,
        105,
        "Korrespondenztabelle Laplace hochgeladen",
        "<p>Die Korrespondenztabelle zur Laplace-Transformation ist jetzt im Kurs. "
        "Sie darf in der Klausur verwendet werden.</p>",
        "Prof. Dr. Erika Musterfrau",
        1,
    ),
    (
        702,
        101,
        "Raumänderung Übung",
        "<p>Die Übung am Donnerstag findet ausnahmsweise in Raum 2-1.10 statt.</p>",
        "Max Mustermann",
        4,
    ),
]


def _file(name: str, course_id: int, module_id: int, modified: datetime) -> FileContent:
    mimetypes = {
        ".pdf": "application/pdf",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    extension = name[name.rfind(".") :]
    return FileContent(
        type="file",
        filename=name,
        fileurl=f"{DEMO_BASE_URL}/webservice/pluginfile.php/{course_id}/{module_id}/{name}",
        filesize=100_000 + module_id * 1_000,
        timemodified=modified,
        mimetype=mimetypes[extension],
    )


class DemoMoodleClient:
    """Implements `MoodleSource` with the invented data above."""

    def __init__(self, now: datetime | None = None) -> None:
        self._now = now or datetime.now(UTC)

    def __repr__(self) -> str:
        return "DemoMoodleClient()"

    def close(self) -> None:
        pass

    def site_info(self) -> SiteInfo:
        return SiteInfo(userid=DEMO_USER_ID, fullname="Demo Studentin", release="4.5 (Demo)")

    def courses(self, user_id: int) -> list[Course]:
        return [
            Course(id=course_id, shortname=shortname, fullname=fullname)
            for course_id, (shortname, fullname, _) in _COURSES.items()
        ]

    def course_contents(self, course_id: int) -> list[Section]:
        if course_id not in _COURSES:
            return []
        sections_by_name = _COURSES[course_id][2]
        sections: list[Section] = []
        for position, (section_name, files) in enumerate(sections_by_name.items()):
            modules = []
            for index, name in enumerate(files):
                module_id = course_id * 100 + position * 10 + index
                modified = self._now - timedelta(days=7 * (len(sections_by_name) - position))
                modules.append(
                    Module(
                        id=module_id,
                        name=name.rsplit(".", 1)[0].replace("_", " "),
                        modname="resource",
                        url=f"{DEMO_BASE_URL}/mod/resource/view.php?id={module_id}",
                        contents=[_file(name, course_id, module_id, modified)],
                    )
                )
            sections.append(
                Section(
                    id=course_id * 10 + position,
                    name=section_name,
                    section=position,
                    modules=modules,
                )
            )
        return sections

    def assignments(self, course_ids: list[int]) -> list[Assignment]:
        return [
            Assignment(
                id=assignment_id,
                cmid=assignment_id + 1000,
                course=course_id,
                name=name,
                duedate=self._now + timedelta(days=due_in_days),
            )
            for assignment_id, course_id, name, due_in_days in _ASSIGNMENTS
            if course_id in course_ids
        ]

    def upcoming_events(self, start: datetime, end: datetime) -> list[Event]:
        events = [
            Event(
                id=assignment.id + 2000,
                name=f"{assignment.name} ist fällig",
                courseid=assignment.course,
                timestart=assignment.duedate,
                url=f"{DEMO_BASE_URL}/mod/assign/view.php?id={assignment.cmid}",
                modulename="assign",
            )
            for assignment in self.assignments(list(_COURSES))
            if assignment.duedate is not None and start <= assignment.duedate <= end
        ]
        return sorted(events, key=lambda event: event.timestart)

    def announcements(self, course_ids: list[int]) -> list[Announcement]:
        return [
            Announcement(
                id=announcement_id,
                courseid=course_id,
                subject=subject,
                message=message,
                author=author,
                created=self._now - timedelta(days=days_ago),
            )
            for announcement_id, course_id, subject, message, author, days_ago in _ANNOUNCEMENTS
            if course_id in course_ids
        ]
