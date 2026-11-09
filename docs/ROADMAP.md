# Roadmap

Grundsatz: **Erst ein dünner, kompletter Durchstich, der jeden Tag Zeit spart – dann erweitern.** Lieber eine Stufe fertig und nutzbar als alle halb.

| Stufe | Ziel | Inhalt | Status |
|---|---|---|---|
| **0** | Machbarkeit | Moodle-API testen | ✔ GO (09.11.2026) |
| **1** | „Ich muss nicht mehr in den Lernraum“ | Sync (Kurse, Dateien, Abgaben, Termine, Ankündigungen), Dashboard „Neu“ + „Fristen“, Telegram-Benachrichtigung | offen |
| **2** | „Frag deine Unterlagen“ | Text aus PDFs, Suchindex (pgvector + Stichwortsuche), MCP-Server lokal in Claude Desktop, **Such-Agent**, **Sortier-Agent** | offen |
| **3** | „Überall verfügbar“ | Hosting (Cloud-Server, HTTPS, Login), MCP von außen (auch Claude-App am Handy), **Wochen-Agent**, **Lern-Agent** | offen |
| **4** | „Meine Notizen“ | GoodNotes-PDFs (Auto-Backup) einbinden, Handschrift-Erkennung | offen |
| **5** | Portfolio | Demo-Screenshots, Architekturdiagramm, Tests/CI, Repo öffentlich | laufend |

## Stufe 1 – Aufgaben

- [ ] Projektgerüst: Docker Compose (app, worker, db), Konfiguration über `.env`
- [ ] Moodle-Client + Demo-Client mit Beispieldaten
- [ ] Datenmodell: Kurse, Abschnitte, Dokumente, Abgaben, Termine, Ankündigungen, Sync-Läufe
- [ ] Sync mit Änderungserkennung (neu / aktualisiert)
- [ ] Dashboard: Start (Fristen + Neu), Kursliste, Kursansicht, Kurse ausblenden
- [ ] Dateien über die App öffnen (Token bleibt auf dem Server)
- [ ] Telegram: neue Inhalte nach jedem Sync, tägliche Fristen-Erinnerung
- [ ] Tests mit Fake-Client, GitHub Actions
- [ ] Erster echter Sync mit dem TH-Lernraum
- [ ] Kursfilter für das aktuelle Semester einstellen
- [ ] Telegram-Bot anlegen und verbinden
- [ ] Eine Woche im Alltag nutzen, Verbesserungen sammeln

## Stufe 2 – Aufgaben (Vorschau)

- [ ] Dateien herunterladen, Text pro Seite extrahieren (PyMuPDF), OCR für Scans
- [ ] Abschnitte bilden, Embeddings mit lokalem mehrsprachigem Modell, pgvector
- [ ] Hybride Suche (Volltext + Vektor), Ergebnis immer mit Datei, Seite, Link
- [ ] MCP-Server (lokal, stdio) mit Tools: `suche`, `fristen`, `neu`, `kurs_inhalt`, `notiz_speichern`
- [ ] Sortier-Agent für Ankündigungen (Haiku, Budget-Limit)
