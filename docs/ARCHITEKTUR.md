# Architektur

## Überblick in vier Schichten

```
┌──────────────────────────────────────────────────────────────────┐
│ 4. ZUGANG       Dashboard (React-PWA, Handy/PC) Claude-App via MCP│
├──────────────────────────────────────────────────────────────────┤
│ 3. LOGIK        FastAPI (/api): Daten, Agenten, Suche, LLM-Schicht│
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
| `app` | `uvicorn app.main:app` | JSON-API unter `/api`, gebautes Frontend als statische Dateien, später MCP |
| `worker` | `python -m app.worker` | Geplante Aufgaben: Sync, Erinnerungen, später Indexierung und Agenten |
| `db` | PostgreSQL 16 + pgvector | Daten und Vektoren |

`app` und `worker` nutzen **dasselbe Image** – ein Code, zwei Startbefehle (modularer Monolith).

Das Image wird mehrstufig gebaut: Stufe 1 baut das Frontend mit Node (`npm run build` → `dist/`), Stufe 2 ist das Python-Image (Abhängigkeiten mit uv) und kopiert `dist/` hinein. Im Betrieb gibt es also **keinen Node-Prozess** – FastAPI liefert die statischen Dateien aus.

## Frontend und API

| Modus | Frontend | API | Aufruf im Browser |
|---|---|---|---|
| Entwicklung | Vite-Dev-Server (`localhost:5173`, Hot Reload) | `uvicorn --reload` (`localhost:8000`) | `localhost:5173`; Vite leitet `/api/*` per Proxy an FastAPI weiter |
| Betrieb | statische Dateien aus `frontend/dist`, von FastAPI ausgeliefert | FastAPI im Container `app` | ein Origin: `/api/*` → API, alles andere → `index.html` (Client-Routing) |

Folgen: kein CORS nötig, ein Container weniger, Login-Schutz gilt für API und Frontend gleichermaßen. Die API-Typen für das Frontend werden aus dem OpenAPI-Schema von FastAPI abgeleitet, damit Backend und Frontend nicht auseinanderlaufen.

## Code-Struktur (Vorschlag)

```
backend/
├── pyproject.toml          Abhängigkeiten (uv), Tool-Einstellungen
├── uv.lock
├── app/
│   ├── main.py             FastAPI-App: Router /api + statisches Frontend
│   ├── config.py           Einstellungen aus .env
│   ├── db.py               Datenbankverbindung
│   ├── models.py           Tabellen
│   ├── api/                JSON-Endpunkte (courses, documents, deadlines, …)
│   ├── moodle/
│   │   ├── client.py       echte Moodle-API
│   │   └── demo.py         Beispieldaten (Demo-Modus, Tests)
│   ├── sync/service.py     Sync mit Änderungserkennung
│   ├── llm/                LLM-Schicht (siehe unten)
│   ├── notify/telegram.py  Benachrichtigungen
│   ├── worker.py           Zeitplan
│   └── cli.py              Befehle: init-db, sync, …
└── tests/                  pytest

frontend/
├── package.json
├── vite.config.ts          Dev-Proxy /api → localhost:8000, PWA
├── index.html
└── src/
    ├── main.tsx
    ├── api/                typisierter Client für /api
    ├── pages/              Start, Kurse, Kursansicht
    └── components/

.github/workflows/          CI (siehe docs/HARNESS.md)
Dockerfile                  mehrstufig: Node baut frontend/ → Python-Image
docker-compose.yml          app, worker, db
```

## LLM-Schicht

Ziel: Der Anbieter ist eine **Einstellung**, keine Code-Änderung. Grund: Es ist offen, ob die TH einen KI-Zugang stellt.

```
Agent (z. B. Sortier-Agent)
        │  ruft nur die eigene Schnittstelle auf
        ▼
app/llm/base.py        LLMClient: complete(system, messages) → Text
        │
        ├── anthropic.py   Adapter für die Anthropic-API
        └── openai.py      Adapter für OpenAI-kompatible APIs (LLM_BASE_URL)
        ▲
app/llm/__init__.py    get_llm(): wählt den Adapter anhand von LLM_PROVIDER
```

| Variable | Bedeutung |
|---|---|
| `LLM_PROVIDER` | `anthropic` oder `openai` (= jede OpenAI-kompatible API) |
| `LLM_BASE_URL` | nur für `openai` nötig, z. B. Endpunkt der TH oder ein lokaler Server |
| `LLM_API_KEY` | Schlüssel des gewählten Anbieters |
| `LLM_MODEL` | Modellname beim Anbieter |

Regeln:
- Nur **ein** Aufrufmuster am Anfang (Text rein, Text raus). Weitere Fähigkeiten (z. B. Tool-Use, Streaming) erst, wenn ein Agent sie wirklich braucht.
- Kein Code außerhalb von `app/llm/` importiert ein Anbieter-SDK.
- Tests nutzen einen Fake-Adapter, damit CI ohne API-Schlüssel läuft.
- Gilt nur für **Hintergrund-Agenten**. Der Chat läuft weiterhin über die Claude-App per MCP (Pro-Abo).

## Worker vs. Agent

| | Worker (fester Code) | Agent (LLM entscheidet) |
|---|---|---|
| Beispiele | Sync, Text extrahieren, Embeddings, Erinnerungen | Suche beantworten, Ankündigungen einordnen, Wochenplan, Lernzettel |
| Verhalten | deterministisch | flexibel |
| Kosten | keine | Pro-Abo (Chat) oder LLM-Schicht (Hintergrund) |

## Agenten

| Agent | Auslöser | Läuft über | Stufe |
|---|---|---|---|
| Such-Agent | deine Frage in Claude | MCP + Pro-Abo | 2 |
| Sortier-Agent | neue Ankündigung | LLM-Schicht (kleines, günstiges Modell) | 2 |
| Wochen-Agent | sonntags | LLM-Schicht | 3 |
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

- Moodle-Token und `LLM_API_KEY` nur in `.env`, nie im Browser: Dateien werden über `/api/files/{id}` vom Server abgeholt.
- Optionaler Login-Schutz (`APP_PASSWORD`, HTTP Basic) schon in Stufe 1; richtiges Login in Stufe 3.
- Nur eigene Daten, Abrufrate moderat.
- Secret-Scan in der CI verhindert, dass Token versehentlich ins Repo gelangen.
