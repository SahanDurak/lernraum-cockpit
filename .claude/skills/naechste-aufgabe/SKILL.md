---
name: naechste-aufgabe
description: Nimmt die nächste offene Aufgabe aus docs/ROADMAP.md und arbeitet sie mit Freigabe ab – auf einem Feature-Branch, mit /feature-dev, Tests, Security-Review und Pull Request.
---
1. Lies CLAUDE.md, docs/ROADMAP.md und die betroffenen Docs.
2. Nimm NUR die erste offene Aufgabe der aktuellen Stufe.
3. Stelle sicher, dass der Arbeitsbaum sauber ist, hole den aktuellen Stand von `main` und lege einen Feature-Branch an (`feat/…`, `fix/…`, `docs/…`, `chore/…`, kurz und auf Englisch). Nie direkt auf `main` arbeiten.
4. Arbeite die Aufgabe mit `/feature-dev` ab. Zeig mir vor dem Umsetzen den Plan (Dateien, Ansatz, woran wir Erfolg erkennen) und WARTE auf mein OK.
5. Setze in kleinen Schritten um.
6. Lass den `tester` laufen, dann den `security-reviewer`. Gefundene Probleme beheben, bevor es weitergeht.
7. Hake die Aufgabe in der ROADMAP ab; neue Entscheidungen in docs/ENTSCHEIDUNGEN.md.
8. Erkläre mir die Änderung in 5 Sätzen.
9. Schlage Commit-Message (Englisch, Conventional Commits) und PR-Titel/-Beschreibung vor und WARTE auf mein OK.
10. Nach OK: committen, Branch pushen, Pull Request gegen `main` öffnen. Nicht selbst mergen – Merge erst nach grüner CI und Review durch mich.
