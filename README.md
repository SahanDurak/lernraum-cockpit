# Lernraum Cockpit

> Mein persönlicher Arbeitsplatz fürs Studium: Alle Inhalte aus dem TH-Lernraum (Moodle) landen automatisch in meiner eigenen App – mit Dashboard für Handy und PC und einem KI-Assistenten (Claude) für Zusammenfassungen, Lernpläne und Fragen an meine Unterlagen.

**Status:** Phase 0 abgeschlossen (Moodle-API getestet: ✔ GO, 09.11.2026) · Stufe 1 in Planung (zuerst: Harness)

---

## Das Problem

- Unterlagen, Ankündigungen und Abgaben sind über 40+ Lernraum-Kurse verteilt.
- Neue Dateien muss man aktiv suchen; Fristen gehen leicht unter.
- Zusammenfassen, Lernpläne erstellen und Fristen planen passiert in getrennten Tools.

## Die Idee

Der Lernraum wird nur noch **Datenquelle im Hintergrund**. Ich arbeite ausschließlich in meiner eigenen, gehosteten App:

1. **Automatischer Sync** holt Kurse, Dateien, Ankündigungen und Abgaben aus dem Lernraum.
2. **Dashboard** (Handy + PC) zeigt: Was ist neu? Was ist diese Woche fällig?
3. **Claude** (über mein Claude-Pro-Abo) greift per MCP auf alle Daten zu: zusammenfassen, Lernpläne, Fragen beantworten – und speichert Ergebnisse zurück in die App.
4. **Hintergrund-Agenten** nutzen eine austauschbare LLM-Schicht (Anthropic oder ein OpenAI-kompatibler Anbieter, z. B. ein möglicher KI-Zugang der TH).

## Architektur (Überblick)

```
TH-Lernraum (Moodle 4.5)
        │  Moodle Web Services API (kostenlos, eigener Token)
        ▼
   Sync-Dienst (stündlich)
        │
        ▼
   Backend (FastAPI, JSON-API /api) + PostgreSQL ──► MCP-Server ──► Claude-App (Pro-Abo, auch mobil)
        │                    │                                  Chat, Zusammenfassungen, Lernpläne
        │                    └──► LLM-Schicht ──► Anthropic | OpenAI-kompatibel
        ▼
   Dashboard (React + Vite + TypeScript + Tailwind, PWA für Handy/PC)
```

Details: [docs/ARCHITEKTUR.md](docs/ARCHITEKTUR.md)

## Tech-Stack

| Bereich | Technik |
|---|---|
| Backend | Python (uv), FastAPI, httpx, PostgreSQL + pgvector |
| Frontend | React, Vite, TypeScript, Tailwind CSS |
| KI | MCP-Server für Claude; LLM-Schicht mit Adaptern für Anthropic und OpenAI-kompatible APIs |
| Betrieb | Docker Compose (`app`, `worker`, `db`) |

## Harness Engineering

Ein Projektziel ist zu zeigen, wie ich mit aktuellen Agent-Workflows entwickle:

- **Claude Code** mit Subagenten (`tester`, `security-reviewer`, `erklaerer`), Skills, Plugins (feature-dev, ralph-loop, code-review, security-guidance) und Hooks
- **CI mit GitHub Actions:** Lint, Typprüfung, Tests, Secret-Scan, Docker-Build
- **Claude-Review** in jedem Pull Request (über das Pro-Abo)
- **Branch Protection** auf `main`, später **CD**

Details: `docs/HARNESS.md` (entsteht als erste Aufgabe in Stufe 1)

## Dokumentation

| Datei | Inhalt |
|---|---|
| [docs/VISION.md](docs/VISION.md) | Was ich will und warum – Ziele, Nicht-Ziele |
| [docs/ANFORDERUNGEN.md](docs/ANFORDERUNGEN.md) | Funktionen nach Priorität |
| [docs/ARCHITEKTUR.md](docs/ARCHITEKTUR.md) | Komponenten, Datenfluss, Technik |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Phasen mit Ergebnissen |
| [docs/ENTSCHEIDUNGEN.md](docs/ENTSCHEIDUNGEN.md) | Getroffene Entscheidungen und offene Fragen |
| [docs/MOODLE_API.md](docs/MOODLE_API.md) | Ergebnisse des API-Tests und genutzte Funktionen |
| `docs/HARNESS.md` | CI, Hooks, Agenten-Workflow mit Diagramm (folgt in Stufe 1) |

## Datenschutz

- Zugangsdaten und Token stehen **nur** in einer lokalen `.env` – niemals im Repository.
- Das öffentliche Repo enthält einen **Demo-Modus mit erfundenen Beispieldaten** für Screenshots.
- Es werden ausschließlich meine eigenen Lernraum-Daten verarbeitet.
