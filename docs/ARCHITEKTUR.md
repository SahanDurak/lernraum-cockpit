# Architektur

## Überblick in vier Schichten

```
┌──────────────────────────────────────────────────────────────────┐
│ 4. ZUGANG       Dashboard (HTMX, Handy/PC)     Claude-App via MCP │
├──────────────────────────────────────────────────────────────────┤
│ 3. LOGIK        FastAPI: Daten aufbereiten, Agenten, Suche        │
├──────────────────────────────────────────────────────────────────┤
│ 2. DATEN        PostgreSQL + pgvector · Dateispeicher             │
├──────────────────────────────────────────────────────────────────┤
│ 1. BESCHAFFUNG  Worker: Sync ◄── Lernraum (Moodle) · GoodNotes    │
└──────────────────────────────────────────────────────────────────┘
```

Jede Schicht hat eine Aufgabe. Eine neue Quelle betrifft nur Schicht 1, ein neues Frontend nur Schicht 4.

## Container

| Container | Startbefehl | Aufgabe |
|---|---|---|
| `app` | `uvicorn app.web.main:app` | Dashboard, API, später MCP |
| `worker` | `python -m app.worker` | Geplante Aufgaben: Sync, Erinnerungen, später Indexierung und Agenten |
| `db` | PostgreSQL 16 + pgvector | Daten und Vektoren |

`app` und `worker` nutzen **dasselbe Image** – ein Code, zwei Startbefehle (modularer Monolith).

## Code-Struktur (Vorschlag)

```
app/
├── config.py           Einstellungen aus .env
├── db.py               Datenbankverbindung
├── models.py           Tabellen
├── moodle/
│   ├── client.py       echte Moodle-API
│   └── demo.py         Beispieldaten (Demo-Modus, Tests)
├── sync/service.py     Sync mit Änderungserkennung
├── notify/telegram.py  Benachrichtigungen
├── web/                Dashboard (FastAPI + Jinja2 + HTMX)
├── worker.py           Zeitplan
└── cli.py              Befehle: init-db, sync, …
```

## Worker vs. Agent

| | Worker (fester Code) | Agent (LLM entscheidet) |
|---|---|---|
| Beispiele | Sync, Text extrahieren, Embeddings, Erinnerungen | Suche beantworten, Ankündigungen einordnen, Wochenplan, Lernzettel |
| Verhalten | deterministisch | flexibel |
| Kosten | keine | Pro-Abo (Chat) oder API (Hintergrund) |

## Agenten

| Agent | Auslöser | Läuft über | Stufe |
|---|---|---|---|
| Such-Agent | deine Frage in Claude | MCP + Pro-Abo | 2 |
| Sortier-Agent | neue Ankündigung | API (Haiku) | 2 |
| Wochen-Agent | sonntags | API (Haiku/Sonnet) | 3 |
| Lern-Agent | deine Anfrage in Claude | MCP + Pro-Abo | 3 |

## Wissenssuche (RAG, Stufe 2)

```
Vorbereitung (Worker)                         Frage (Claude über MCP)
Datei → Text pro Seite → Abschnitte           Frage → hybride Suche
→ Embedding (lokal) → pgvector                → passendste Abschnitte (mit Datei, Seite, Link)
                                              → Claude antwortet NUR daraus, mit Quellen
```

Regeln: Stichwort- + Bedeutungssuche kombiniert · jede Aussage mit Quelle · „nicht gefunden“ statt raten.

## Datenmodell (Stufe 1)

| Tabelle | Wichtigste Felder |
|---|---|
| `courses` | moodle_id, fullname, shortname, hidden, last_synced_at |
| `sections` | moodle_id, course_id, name, position |
| `documents` | moodle_id (Datei-URL), course_id, section_id, module_name, filename, mimetype, filesize, time_modified, first_seen_at, is_new, is_updated |
| `assignments` | moodle_id, course_id, name, due_at, url |
| `events` | moodle_id, course_id, name, starts_at, url |
| `announcements` | moodle_id, course_id, subject, message, author, posted_at, is_new |
| `sync_runs` | started_at, finished_at, new_documents, new_announcements, error |

## Sicherheit

- Moodle-Token nur in `.env`, nie im Browser: Dateien werden über `/datei/{id}` vom Server abgeholt.
- Optionaler Login-Schutz (`APP_PASSWORD`, HTTP Basic) schon in Stufe 1; richtiges Login in Stufe 3.
- Nur eigene Daten, Abrufrate moderat.
