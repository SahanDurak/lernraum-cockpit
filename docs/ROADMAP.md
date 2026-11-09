# Roadmap

Grundsatz: **Erst ein dünner, kompletter Durchstich, der jeden Tag Zeit spart – dann erweitern.** Lieber eine Stufe fertig und nutzbar als alle halb.

| Stufe | Ziel | Inhalt | Status |
|---|---|---|---|
| **0** | Machbarkeit | Moodle-API testen | ✔ GO (09.11.2026) |
| **1** | „Ich muss nicht mehr in den Lernraum“ | **Harness** (CI, Hooks, Branch Protection), Sync (Kurse, Dateien, Abgaben, Termine, Ankündigungen), Dashboard „Neu“ + „Fristen“, Telegram-Benachrichtigung | offen |
| **2** | „Frag deine Unterlagen“ | Text aus PDFs, Suchindex (pgvector + Stichwortsuche), MCP-Server lokal in Claude Desktop, **Such-Agent**, **Sortier-Agent** | offen |
| **3** | „Überall verfügbar“ | Hosting (Cloud-Server, HTTPS, Login), **CD** (automatisches Deployment), MCP von außen (auch Claude-App am Handy), **Wochen-Agent**, **Lern-Agent** | offen |
| **4** | „Meine Notizen“ | GoodNotes-PDFs (Auto-Backup) einbinden, Handschrift-Erkennung | offen |
| **5** | Portfolio | Demo-Screenshots, Architekturdiagramm, Harness-Doku, Repo öffentlich | laufend |

## Stufe 1 – Aufgaben

- [x] **Harness aufbauen** (vor dem App-Gerüst) – siehe `docs/HARNESS.md`:
  - GitHub Actions: Lint, Typen, Tests, Secret-Scan, Docker-Build (Jobs laufen, sobald `backend/`/`frontend/` existieren)
  - Claude-Review in Pull Requests über das Pro-Abo
  - Claude-Code-Hooks (z. B. Formatieren nach Änderungen, `.env` schützen)
  - Branch Protection auf `main`: lokal (git-`pre-push`- und Claude-Hook), GitHub-seitig siehe nächste Aufgabe
  - `docs/HARNESS.md` mit Diagramm: Subagenten, Skills, Plugins, Hooks, CI, Review-Ablauf
- [x] **Branch Protection auf GitHub** (Repo öffentlich statt GitHub Pro, 09.11.2026): Ruleset `protect-main` – Merge nur per PR, required checks `ci` + `secret-scan`, keine Force-Pushes, kein Löschen von `main`, offene Kommentare müssen erledigt sein; Secret Scanning mit Push Protection, Dependabot-Alerts; `claude.yml` auf `contents: write` umgestellt, damit `@claude` Code ändern kann
- [x] Projektgerüst: `backend/` (FastAPI, uv) + `frontend/` (React, Vite, TypeScript, Tailwind), Docker Compose (app, worker, db), mehrstufiges Dockerfile, Konfiguration über `.env` – mit `/api/health`, Healthchecks, Versionen gepinnt (`.nvmrc`, `.python-version`, Image-Digests), Dependabot für uv/npm/Docker
- [ ] Moodle-Client + Demo-Client mit Beispieldaten
- [ ] Datenmodell: Kurse, Abschnitte, Dokumente, Abgaben, Termine, Ankündigungen, Sync-Läufe
- [ ] Sync mit Änderungserkennung (neu / aktualisiert)
- [ ] JSON-API unter `/api` für Kurse, Dokumente, Fristen, Neuigkeiten
- [ ] Dashboard (React-PWA): Start (Fristen + Neu), Kursliste, Kursansicht, Kurse ausblenden
- [ ] Dateien über die App öffnen (Token bleibt auf dem Server)
- [ ] Telegram: neue Inhalte nach jedem Sync, tägliche Fristen-Erinnerung
- [ ] Tests mit Fake-Client (pytest) und Frontend-Tests (Vitest), in der CI
- [ ] Erster echter Sync mit dem TH-Lernraum
- [ ] Kursfilter für das aktuelle Semester einstellen
- [ ] Telegram-Bot anlegen und verbinden
- [ ] Eine Woche im Alltag nutzen, Verbesserungen sammeln

## Stufe 2 – Aufgaben (Vorschau)

- [ ] Dateien herunterladen, Text pro Seite extrahieren (PyMuPDF), OCR für Scans
- [ ] Abschnitte bilden, Embeddings mit lokalem mehrsprachigem Modell, pgvector
- [ ] Hybride Suche (Volltext + Vektor), Ergebnis immer mit Datei, Seite, Link
- [ ] MCP-Server (lokal, stdio) mit Tools: `suche`, `fristen`, `neu`, `kurs_inhalt`, `notiz_speichern`
- [ ] LLM-Schicht: Schnittstelle + Adapter Anthropic und OpenAI-kompatibel, Fake-Adapter für Tests
- [ ] Sortier-Agent für Ankündigungen (über die LLM-Schicht, Budget-Limit)

## Offen

- [ ] Ruleset für Tags und übrige Branches: `protect-main` schützt nur `main`; Tags (Erstellen/Löschen/Force-Push) und Feature-Branches (Force-Push, Löschen) sind ungeschützt – auch gegenüber `@claude` mit Schreibrechten
- [ ] `persist-credentials: false` in `claude.yml` und `claude-review.yml` testen: Ohne die Option bleibt der Token im Checkout (`.git/config`) liegen; nur übernehmen, wenn die Claude-Action ihre Git-Authentifizierung trotzdem selbst einrichtet
