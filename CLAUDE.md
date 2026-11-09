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
- LLM-Aufrufe nur über die eigene LLM-Schicht (`backend/app/llm/`), nie direkt ein Anbieter-SDK im übrigen Code.
- Immer auf Feature-Branches arbeiten, nie direkt auf `main`. Merge nach `main` nur per Pull Request (mit grüner CI, sobald sie existiert). Ablauf: Skill `naechste-aufgabe`.
- Commit- und PR-Texte nie inline (`-m`, `--body`): Text mit dem Write-Tool nach `.git/COMMIT_MSG_DRAFT` bzw. `.git/PR_BODY_DRAFT` schreiben, dann `git commit -F .git/COMMIT_MSG_DRAFT && rm .git/COMMIT_MSG_DRAFT` bzw. `gh pr create --title "…" --body-file .git/PR_BODY_DRAFT && rm .git/PR_BODY_DRAFT` (aus dem Repo-Root). Der PR-Titel bleibt inline, also ohne den Dateinamen `.env`. Grund: `docs/HARNESS.md`.

## Stack (Stand 09.11.2026)
- Backend: Python (uv), FastAPI (JSON-API unter `/api`), PostgreSQL + pgvector, httpx – Code in `backend/`
- Frontend: React + Vite + TypeScript + Tailwind (PWA) – Code in `frontend/`
- Im Betrieb liefert FastAPI das gebaute Frontend als statische Dateien aus; im Dev-Modus läuft Vite mit Proxy auf `/api`.
- LLM: austauschbar über `LLM_PROVIDER` (Adapter `anthropic` oder `openai`-kompatibel)
- Betrieb: Docker Compose mit `app`, `worker`, `db`
- Harness: CI mit GitHub Actions, Claude-Hooks, Subagenten, Skills, Plugins – siehe `docs/HARNESS.md` (entsteht in Stufe 1)

## Arbeitsweise (nach Karpathys Coding-Regeln)
1. **Erst denken, dann coden:** Annahmen nennen, bei Unklarheit fragen statt raten.
2. **So einfach wie möglich:** kein Code „für später“, keine unnötigen Abstraktionen.
3. **Gezielte Änderungen:** nur anfassen, was die Aufgabe braucht; nichts nebenbei umbauen.
4. **Ziel vorher festlegen:** vor dem Umsetzen sagen, woran wir erkennen, dass es funktioniert (Test oder Prüfschritt).
