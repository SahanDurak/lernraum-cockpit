# Anforderungen

Priorität: **M** = Muss (MVP) · **S** = Soll · **K** = Kann (später)

## 1. Lernraum-Sync

| # | Anforderung | Prio |
|---|---|---|
| 1.1 | Alle eingeschriebenen Kurse abrufen; Kurse ausblenden/archivieren können (z. B. alte Semester, FB-Infokurse) | M |
| 1.2 | Kursinhalte (Abschnitte, Dateien, Links) abrufen und Dateien lokal speichern | M |
| 1.3 | Abgaben (Assignments) mit Fälligkeitsdatum abrufen | M |
| 1.4 | Kalendertermine abrufen | M |
| 1.5 | Ankündigungen (Forum-Beiträge der Kurse) abrufen | M |
| 1.6 | Sync automatisch, z. B. stündlich; nur Änderungen übertragen | M |
| 1.7 | Erkennen, was seit dem letzten Sync **neu** oder **geändert** ist | M |
| 1.8 | Quiz-Termine abrufen | S |

## 2. Dashboard (Handy + PC)

| # | Anforderung | Prio |
|---|---|---|
| 2.1 | Startseite „Heute / Diese Woche“: Fristen, Termine, eigene Aufgaben | M |
| 2.2 | „Neu seit letztem Besuch“: neue Dateien und Ankündigungen aller Kurse | M |
| 2.3 | Kursansicht mit allen Unterlagen, nach Abschnitt sortiert | M |
| 2.4 | Volltextsuche und Filter (Kurs, Typ, Datum) | S |
| 2.5 | Als App auf dem Homescreen installierbar (PWA), mobil gut bedienbar | M |
| 2.6 | Eigene Aufgaben anlegen und abhaken | S |
| 2.7 | Dateien direkt in der App öffnen | S |
| 2.8 | Dunkelmodus | K |

## 3. KI-Funktionen (über Claude)

| # | Anforderung | Prio |
|---|---|---|
| 3.1 | MCP-Server, über den Claude Kurse, Dateien, Fristen und Aufgaben lesen kann | S |
| 3.2 | Claude kann Zusammenfassungen und Notizen zurück in die App speichern | S |
| 3.3 | Zusammenfassungen werden im Dashboard beim jeweiligen Dokument angezeigt | S |
| 3.4 | Lernplan bis zu einem Prüfungstermin erstellen lassen | K |
| 3.5 | Lernzettel / Quizfragen aus Unterlagen erzeugen | K |
| 3.6 | Semantische Suche über alle Unterlagen (pgvector) | K |
| 3.7 | Automatische Zusammenfassung neuer Dateien im Hintergrund (Claude-API, Budget-Limit) | K |

## 4. Benachrichtigungen und Automationen

| # | Anforderung | Prio |
|---|---|---|
| 4.1 | Benachrichtigung bei neuer Datei / Ankündigung (z. B. Telegram oder Push) | S |
| 4.2 | Erinnerung X Tage vor einer Frist | S |
| 4.3 | Wochenüberblick am Sonntag | K |

## 5. Betrieb und Qualität

| # | Anforderung | Prio |
|---|---|---|
| 5.1 | Start mit einem Befehl (`docker compose up`) | M |
| 5.2 | Zugangsdaten nur in `.env`, nie im Repo; Token verschlüsselt bzw. geschützt | M |
| 5.3 | Login-Schutz für die gehostete App | M |
| 5.4 | Demo-Modus mit Beispieldaten | S |
| 5.5 | Automatische Tests + GitHub Actions | S |
| 5.6 | README mit Architekturdiagramm und Screenshots | M |
