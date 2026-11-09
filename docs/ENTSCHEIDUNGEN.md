# Entscheidungen

## Getroffen

| Datum | Entscheidung | Begründung |
|---|---|---|
| 09.11.2026 | Eigene, gehostete App ist der Arbeitsplatz; Lernraum nur Datenquelle | Alles an einem Ort; Portfolio-Projekt |
| 09.11.2026 | Moodle-Anbindung über offizielle Web Services (Token wie Moodle-App), kein Scraping | Stabil, offiziell, getestet |
| 09.11.2026 | Keine Noten / kein QIS | Noten bleiben im QIS; keine offizielle Schnittstelle |
| 09.11.2026 | **Modularer Monolith**: ein Code, Container `app`, `worker`, `db` | Einfach für einen Nutzer; Worker blockiert nie das Dashboard |
| 09.11.2026 | **PostgreSQL + pgvector** | Bekannt, Industriestandard, Vektorsuche eingebaut |
| 09.11.2026 | **Worker (fester Code) für alles Regelbasierte, Agenten (LLM) nur wo Verstehen nötig ist** | Zuverlässig, günstig; Agenten dort, wo sie Mehrwert bringen |
| 09.11.2026 | **RAG als Kern** der Wissenssuche: Antworten nur aus gefundenen Stellen, immer mit Quelle; „nicht gefunden“ erlaubt | Überprüfbar statt geraten |
| 09.11.2026 | Embeddings mit lokalem mehrsprachigem Modell | Kostenlos, versteht Deutsch |
| 09.11.2026 | **Kein eigener Chat**: Claude-App über MCP (Pro-Abo) | Besser als selbst gebaut, keine Zusatzkosten, auch mobil |
| 09.11.2026 | MCP **zuerst lokal** (Claude Desktop), später remote | Spart die komplexe Absicherung am Anfang |
| 09.11.2026 | Claude-API nur für Hintergrund-Agenten, Haiku, Budget-Limit | Pro-Abo enthält keine API-Nutzung; Kosten < 2 €/Monat erwartet. *Ergänzt am 09.11.2026: Anbieter austauschbar, siehe LLM-Schicht unten* |
| 09.11.2026 | ~~**Dashboard mit FastAPI + Jinja2 + HTMX + Tailwind** statt Next.js~~ – *ersetzt am 09.11.2026, siehe React + Vite unten* | Eine Sprache, halber Aufwand, mobil gut; für AI-Engineering zählt Backend/KI mehr als React |
| 09.11.2026 | **Hosting auf kleinem Cloud-Server** (z. B. Hetzner) in Stufe 3 | Zuverlässiger und einfacher als Home-Server + Tunnel |
| 09.11.2026 | Benachrichtigungen über **Telegram-Bot** | Am einfachsten, funktioniert sofort am Handy |
| 09.11.2026 | Notizen: **GoodNotes behalten**, PDFs per Auto-Backup einbinden (Stufe 4) | Tool passt sich dem Lernstil an, nicht umgekehrt |
| 09.11.2026 | Stufenweiser Aufbau, mit Claude Code; nach jedem Schritt erklären lassen | Schnell fertig und trotzdem verstanden |
| 09.11.2026 | Entwicklung auf dem privaten Rechner (WSL), nicht auf dem Firmen-Laptop | Privates Projekt, privater Token, private Git-Identität |
| 09.11.2026 | **Frontend: React + Vite + TypeScript + Tailwind** (ersetzt HTMX) | Gängiger Industriestandard, typsichere Oberfläche, gute PWA-Unterstützung; zeigt Full-Stack-Fähigkeiten im Portfolio |
| 09.11.2026 | **FastAPI liefert JSON-API unter `/api`** und im Betrieb das gebaute Frontend als statische Dateien; im Dev-Modus Vite mit Proxy | Ein Origin, kein CORS, kein zusätzlicher Container; Container bleiben `app`, `worker`, `db` |
| 09.11.2026 | Code getrennt in `backend/` und `frontend/` | Klare Grenzen, eigene Tools je Sprache (uv / npm), getrennte CI-Jobs |
| 09.11.2026 | **Python-Abhängigkeiten mit uv** (`pyproject.toml` + `uv.lock`) | Schnell, reproduzierbar per Lockfile, ein Tool für Venv und Pakete |
| 09.11.2026 | **LLM-Anbieter austauschbar**: eigene kleine Schnittstelle mit zwei Adaptern (Anthropic, OpenAI-kompatibel), Auswahl über `.env` (`LLM_PROVIDER`, `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`) | Unklar, ob die TH einen KI-Zugang stellt; OpenAI-kompatibel deckt viele Anbieter ab (auch selbst gehostete). Nur so viel Abstraktion wie für zwei Adapter nötig |
| 09.11.2026 | **Harness Engineering als Projektziel**: Subagenten, Skills, Plugins (feature-dev, ralph-loop, code-review, security-guidance), Hooks, CI mit GitHub Actions, Claude-Review in PRs, Branch Protection, später CD | Projekt soll zeigen, dass ich Agent-Workflows mit aktuellen Mitteln einsetze; Qualität wird automatisch geprüft statt nur versprochen |
| 09.11.2026 | **CI-Prüfungen**: Lint, Typen, Tests, Secret-Scan, Docker-Build – für Backend und Frontend | Fehler und versehentlich eingecheckte Secrets fallen vor dem Merge auf |
| 09.11.2026 | **Claude-Review in Pull Requests über das Pro-Abo** (OAuth-Token als GitHub-Secret, nicht über die API) | Keine zusätzlichen API-Kosten |
| 09.11.2026 | **Python-Typprüfung mit pyright** (statt mypy) | Editor (LSP-Plugin) und CI prüfen mit demselben Werkzeug – keine abweichenden Ergebnisse |
| 09.11.2026 | **Immer Feature-Branch + Pull Request**, auch für Doku; Ablauf im Skill `naechste-aufgabe` | Jede Änderung läuft durch CI und Review; nachvollziehbare Historie |
| 09.11.2026 | **Harness zuerst**: erste Aufgabe in Stufe 1 ist CI, Hooks, Branch Protection und `docs/HARNESS.md`, noch vor dem App-Gerüst | Jeder spätere Schritt läuft dann schon durch dieselben Prüfungen |

## Offen

| Frage | Stand |
|---|---|
| KI-Zugang über die TH (API) | Anfrage an Prof. Knuth gestellt; durch die LLM-Schicht kein Blocker mehr |
| Konkrete Tools für Lint/Secret-Scan (z. B. ruff, ESLint, gitleaks); Typen fest: pyright + tsc | festlegen in der Aufgabe „Harness aufbauen“ |
| CD: wohin und wie deployen | klären mit Stufe 3 (Hosting) |
| GoodNotes: welches Gerät, welche Cloud für das Auto-Backup? | klären vor Stufe 4 |
| Datenbank-Migrationen (Alembic) | einführen, sobald sich das Datenmodell stabilisiert |
