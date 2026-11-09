from datetime import UTC, datetime, timedelta
from urllib.parse import urlparse

from app.moodle.demo import DemoMoodleClient
from app.moodle.schemas import MoodleSource

NOW = datetime(2026, 11, 9, 12, tzinfo=UTC)
DEMO_HOST = "lernraum.demo.invalid"


def make_demo() -> DemoMoodleClient:
    return DemoMoodleClient(now=NOW)


def all_course_ids(demo: DemoMoodleClient) -> list[int]:
    return [course.id for course in demo.courses(demo.site_info().userid)]


def test_is_a_moodle_source() -> None:
    source: MoodleSource = make_demo()  # pyright checks the protocol here
    source.close()


def test_five_courses_including_control_engineering() -> None:
    demo = make_demo()
    courses = demo.courses(demo.site_info().userid)
    assert len(courses) == 5
    assert "Regelungstechnik (ACS)" in [course.fullname for course in courses]


def test_control_engineering_has_laplace_files() -> None:
    demo = make_demo()
    course = next(c for c in demo.courses(1) if c.fullname == "Regelungstechnik (ACS)")
    filenames = [
        file.filename
        for section in demo.course_contents(course.id)
        for module in section.modules
        for file in module.contents
    ]
    assert any("Laplace" in name for name in filenames)


def test_every_course_has_sections_with_files() -> None:
    demo = make_demo()
    for course_id in all_course_ids(demo):
        sections = demo.course_contents(course_id)
        assert sections, course_id
        for section in sections:
            files = [file for module in section.modules for file in module.contents]
            assert files, (course_id, section.name)
            for file in files:
                assert file.timemodified is not None and file.timemodified <= NOW


def test_unknown_course_has_no_contents() -> None:
    assert make_demo().course_contents(999_999) == []


def test_assignments_filtered_by_course_ids() -> None:
    demo = make_demo()
    ids = all_course_ids(demo)
    everything = demo.assignments(ids)
    assert everything
    first_course = everything[0].course
    filtered = demo.assignments([first_course])
    assert filtered
    assert all(a.course == first_course for a in filtered)
    assert demo.assignments([]) == []


def test_upcoming_events_within_range_sorted_and_relative_to_now() -> None:
    demo = make_demo()
    start, end = NOW, NOW + timedelta(days=30)
    events = demo.upcoming_events(start, end)

    assert events, "demo must always have future deadlines"
    assert all(start <= event.timestart <= end for event in events)
    assert [e.timestart for e in events] == sorted(e.timestart for e in events)

    # Past deadlines (before now) are not in a range starting at now.
    past = [a for a in demo.assignments(all_course_ids(demo)) if a.duedate and a.duedate < NOW]
    assert past
    assert not {a.id for a in past} & {e.id - 2000 for e in events}


def test_upcoming_events_empty_outside_range() -> None:
    demo = make_demo()
    far_future = NOW + timedelta(days=3650)
    assert demo.upcoming_events(far_future, far_future + timedelta(days=1)) == []


def test_announcements_filtered_by_course_ids() -> None:
    demo = make_demo()
    everything = demo.announcements(all_course_ids(demo))
    assert everything
    assert all(a.created <= NOW for a in everything)
    course_id = everything[0].courseid
    assert all(a.courseid == course_id for a in demo.announcements([course_id]))
    assert demo.announcements([]) == []


def test_all_urls_use_invalid_host() -> None:
    demo = make_demo()
    ids = all_course_ids(demo)
    urls = [
        url
        for course_id in ids
        for section in demo.course_contents(course_id)
        for module in section.modules
        for url in [module.url, *(file.fileurl for file in module.contents)]
    ]
    urls += [
        event.url
        for event in demo.upcoming_events(NOW - timedelta(days=365), NOW + timedelta(days=365))
    ]
    assert urls
    for url in urls:
        parsed = urlparse(url)
        assert parsed.hostname == DEMO_HOST, url
        assert parsed.hostname is not None and parsed.hostname.endswith(".invalid")
