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
| 09.11.2026 | **Lint/Format: ruff (Python), ESLint + Prettier (TypeScript); Secret-Scan: gitleaks** | Jeweils der verbreitete Standard; ruff ersetzt Linter und Formatter in einem Tool |
| 09.11.2026 | **Secret-Scan doppelt**: gitleaks als git-`pre-commit`-Hook und in der CI (ganze Historie) | Lokal wird ein Secret gar nicht erst committet; die CI fängt alles ab, was am Hook vorbeikommt |
| 09.11.2026 | **Branch Protection vorerst lokal**: git-`pre-push`-Hook + Claude-Hook blocken Pushes auf `main` – *ergänzt am 09.11.2026: GitHub-seitig per Ruleset, siehe „Repo öffentlich“ unten; die lokalen Hooks bleiben als zusätzliche Schicht* | Im Free-Plan für private Repos nicht verfügbar; echte Branch Protection folgt mit GitHub Pro (Student Pack beantragt) |
| 09.11.2026 | **Ein Sammel-Check `ci`** statt einzelner Jobs als required check | Required checks bleiben stabil, auch wenn Jobs dazukommen oder übersprungen werden |
| 09.11.2026 | **Claude-Review nur beim Öffnen / `ready_for_review`**, keine Drafts; erneut per „@claude review“; nur für den Repo-Owner; Limits über `--max-turns`, Timeout, `concurrency` | Spart Pro-Kontingent; nichts läuft endlos |
| 09.11.2026 | ~~**`@claude` vorerst nur lesend** (`contents: read`): kommentiert und reviewt, ändert keinen Code; `write` erst mit Branch Protection~~ – *ersetzt am 09.11.2026: `contents: write`, siehe unten* | Ohne Branch Protection könnte der Workflow technisch direkt auf `main` schreiben |
| 09.11.2026 | **gitleaks immer mit `--redact`** und nur über Git (`gitleaks git`, `--staged`), **nie über den Arbeitsordner** (`gitleaks dir`); `protect.py` erzwingt das | Der Arbeitsordner enthält die echte `.env`; Secrets sollen nie in einer Ausgabe landen |
| 09.11.2026 | **GitHub Actions auf Commit-SHAs gepinnt**, Updates per Dependabot; gitleaks-Download per Prüfsumme verifiziert | Schutz vor umgehängten Tags und manipulierten Downloads (Supply Chain) |
| 09.11.2026 | **Repo öffentlich statt auf GitHub Pro (Student Pack) zu warten**; Branch Protection als Ruleset `protect-main`: Merge nur per PR, required checks `ci` + `secret-scan` (Branch muss aktuell sein), keine Force-Pushes, kein Löschen, offene Kommentare müssen erledigt sein, keine Bypass-Akteure; dazu `delete_branch_on_merge`, Secret Scanning mit Push Protection, Dependabot-Alerts | Für öffentliche Repos ist das alles kostenlos – kein Warten auf das Student Pack. Ein öffentliches Repo war ohnehin Ziel (Stufe 5, Portfolio). Risiko gering: Secrets nur in `.env`, Demo-Daten statt echter Lernraum-Daten, gitleaks lokal + CI, zusätzlich GitHubs Push Protection |
| 09.11.2026 | **`@claude` mit `contents: write`**: darf auf eigene `claude/…`-Branches pushen, `main` schützt das Ruleset; läuft nur auf Issues/PRs, die der Owner selbst angelegt hat (keine fremden Forks) | Seit es Branch Protection gibt, kann der Workflow nicht mehr direkt auf `main` schreiben. Im öffentlichen Repo könnten fremde Issue-Texte oder Fork-Code Claude sonst per Prompt-Injection steuern – mit Schreibrechten und Token |
| 09.11.2026 | **Claude GitHub App behält „Workflows: read/write“** (geprüft und bewusst akzeptiert) | `@claude` kann damit auch Workflow-Dateien auf eigenen Branches ändern; nach `main` kommt nichts ohne PR, grüne CI und mein Review |
| 09.11.2026 | **Lokaler `pre-push`-Hook bleibt** zusätzlich zur Branch Protection | Fällt schon vor dem Push auf statt erst als Ablehnung von GitHub; kostet nichts |

## Offen

| Frage | Stand |
|---|---|
| KI-Zugang über die TH (API) | Anfrage an Prof. Knuth gestellt; durch die LLM-Schicht kein Blocker mehr |
| CD: wohin und wie deployen | klären mit Stufe 3 (Hosting) |
| GoodNotes: welches Gerät, welche Cloud für das Auto-Backup? | klären vor Stufe 4 |
| Datenbank-Migrationen (Alembic) | einführen, sobald sich das Datenmodell stabilisiert |
