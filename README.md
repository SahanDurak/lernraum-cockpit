# Lernraum Cockpit

> Mein persönlicher Arbeitsplatz fürs Studium: Alle Inhalte aus dem TH-Lernraum (Moodle) landen automatisch in meiner eigenen App – mit Dashboard für Handy und PC und einem KI-Assistenten (Claude) für Zusammenfassungen, Lernpläne und Fragen an meine Unterlagen.

**Status:** Phase 0 abgeschlossen (Moodle-API getestet: ✔ GO, 09.11.2026) · Phase 1 in Planung

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

## Architektur (Überblick)

```
TH-Lernraum (Moodle 4.5)
        │  Moodle Web Services API (kostenlos, eigener Token)
        ▼
   Sync-Dienst (stündlich)
        │
        ▼
   Backend + Datenbank ───────────────► MCP-Server ──► Claude-App (Pro-Abo, auch mobil)
        │                                                Chat, Zusammenfassungen, Lernpläne
        ▼
   Dashboard (Web-App, auf Handy/PC installierbar)
```

Details: [docs/ARCHITEKTUR.md](docs/ARCHITEKTUR.md)

## Dokumentation

| Datei | Inhalt |
|---|---|
| [docs/VISION.md](docs/VISION.md) | Was ich will und warum – Ziele, Nicht-Ziele |
| [docs/ANFORDERUNGEN.md](docs/ANFORDERUNGEN.md) | Funktionen nach Priorität |
| [docs/ARCHITEKTUR.md](docs/ARCHITEKTUR.md) | Komponenten, Datenfluss, Technik |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Phasen mit Ergebnissen |
| [docs/ENTSCHEIDUNGEN.md](docs/ENTSCHEIDUNGEN.md) | Getroffene Entscheidungen und offene Fragen |
| [docs/MOODLE_API.md](docs/MOODLE_API.md) | Ergebnisse des API-Tests und genutzte Funktionen |

## Datenschutz

- Zugangsdaten und Token stehen **nur** in einer lokalen `.env` – niemals im Repository.
- Das öffentliche Repo enthält einen **Demo-Modus mit erfundenen Beispieldaten** für Screenshots.
- Es werden ausschließlich meine eigenen Lernraum-Daten verarbeitet.
