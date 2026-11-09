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
| 09.11.2026 | Claude-API nur für Hintergrund-Agenten, Haiku, Budget-Limit | Pro-Abo enthält keine API-Nutzung; Kosten < 2 €/Monat erwartet |
| 09.11.2026 | **Dashboard mit FastAPI + Jinja2 + HTMX + Tailwind** statt Next.js | Eine Sprache, halber Aufwand, mobil gut; für AI-Engineering zählt Backend/KI mehr als React |
| 09.11.2026 | **Hosting auf kleinem Cloud-Server** (z. B. Hetzner) in Stufe 3 | Zuverlässiger und einfacher als Home-Server + Tunnel |
| 09.11.2026 | Benachrichtigungen über **Telegram-Bot** | Am einfachsten, funktioniert sofort am Handy |
| 09.11.2026 | Notizen: **GoodNotes behalten**, PDFs per Auto-Backup einbinden (Stufe 4) | Tool passt sich dem Lernstil an, nicht umgekehrt |
| 09.11.2026 | Stufenweiser Aufbau, mit Claude Code; nach jedem Schritt erklären lassen | Schnell fertig und trotzdem verstanden |
| 09.11.2026 | Entwicklung auf dem privaten Rechner (WSL), nicht auf dem Firmen-Laptop | Privates Projekt, privater Token, private Git-Identität |

## Offen

| Frage | Stand |
|---|---|
| KI-Zugang über die TH (API) | Anfrage an Prof. Knuth gestellt |
| GoodNotes: welches Gerät, welche Cloud für das Auto-Backup? | klären vor Stufe 4 |
| Datenbank-Migrationen (Alembic) | einführen, sobald sich das Datenmodell stabilisiert |
