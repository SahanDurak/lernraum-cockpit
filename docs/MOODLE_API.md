# Moodle API – TH-Lernraum

## Testergebnis Phase 0 (09.11.2026)

| Test | Ergebnis |
|---|---|
| Token über `/login/token.php` (`service=moodle_mobile_app`) | ✔ |
| `core_webservice_get_site_info` | ✔ Moodle 4.5.15+ |
| `core_enrol_get_users_courses` | ✔ 43 Kurse |
| `core_course_get_contents` | ✔ Abschnitte und Dateien |
| `core_calendar_get_action_events_by_timesort` | ✔ (0 Termine in den nächsten 30 Tagen) |

Hinweise:
- Die Seite „Sicherheitsschlüssel“ zeigt nur den RSS-Token; der App-Token ist dort nicht sichtbar.
- Der Browser-Login-Weg (`admin/tool/mobile/launch.php`) liefert 404 → Token nur über `login/token.php`.

## Endpunkte

- Token: `POST https://lernraum.th-luebeck.de/login/token.php` mit `username`, `password`, `service=moodle_mobile_app`
- API: `https://lernraum.th-luebeck.de/webservice/rest/server.php?wstoken=…&wsfunction=…&moodlewsrestformat=json`

## Geplante Funktionen

| Zweck | Funktion | Getestet |
|---|---|---|
| Nutzer-Info | `core_webservice_get_site_info` | ✔ |
| Kurse | `core_enrol_get_users_courses` | ✔ |
| Kursinhalte, Dateien | `core_course_get_contents` | ✔ |
| Termine | `core_calendar_get_action_events_by_timesort` | ✔ |
| Abgaben | `mod_assign_get_assignments` | offen |
| Ankündigungen | `mod_forum_get_forums_by_courses` + `mod_forum_get_forum_discussions` | offen |
| Quizze | `mod_quiz_get_quizzes_by_courses` | offen |
| Datei-Download | `<fileurl>?token=…` | offen |

## Sicherheit

- Der Token wirkt wie ein Passwort. Speicherung nur in `.env` (Rechte 600), nie im Repo.
- Ungültig machen: in der Moodle-App abmelden bzw. TH-Passwort ändern.
- Nur eigene Daten; Abrufrate moderat (z. B. stündlich), um den Lernraum nicht zu belasten.
