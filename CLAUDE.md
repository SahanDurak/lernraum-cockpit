# Hinweise für Claude Code

## Projekt
Lernraum Cockpit: persönliches Studien-Cockpit. Synchronisiert den TH-Lernraum (Moodle 4.5) über die offiziellen Web Services in eine eigene App mit Dashboard (Handy/PC) und MCP-Server für Claude. Vision, Anforderungen und Entscheidungen stehen in `docs/` – vor größeren Änderungen lesen.

## Über mich als Entwickler
- Studiere Wirtschaftsingenieurwesen, arbeite als Software/AI Engineer. Verstehe System Design gut, will meine Programmierfähigkeiten verbessern.
- Erkläre Änderungen kurz und verständlich auf Deutsch. Code und Commits auf Englisch.
- Entwicklung unter Windows mit WSL.

## Regeln
- **Niemals** Token, Passwörter oder echte Lernraum-Daten committen. Zugangsdaten nur aus `.env`.
- Nur offizielle Moodle-Web-Services, kein Scraping. Abrufrate moderat halten.
- Kleine, nachvollziehbare Schritte; nach jedem Schritt testen.
- Neue Entscheidungen in `docs/ENTSCHEIDUNGEN.md` festhalten, Fortschritt in `docs/ROADMAP.md`.

## Stack (Stand Phase 0)
- Backend: Python, FastAPI, PostgreSQL, httpx
- Frontend: noch offen (siehe docs/ENTSCHEIDUNGEN.md)
- Betrieb: Docker Compose
