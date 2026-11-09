# Harness

Der Harness ist alles um den Code herum, was Qualität **automatisch** prüft statt sie nur zu versprechen: Agenten-Workflow in Claude Code, lokale Schutzmechanismen, CI und Review auf GitHub.

## Ablauf einer Änderung

```mermaid
flowchart TD
    A["/naechste-aufgabe<br/>(Skill)"] --> B["Feature-Branch<br/>feat/… fix/… docs/… chore/…"]
    B --> C["/feature-dev (Plugin)<br/>Plan → OK → Umsetzung"]
    C --> D{{"Claude-Code-Hooks<br/>protect.py: .env + main blockiert<br/>format.py: ruff / Prettier"}}
    D --> E["Subagenten<br/>tester → security-reviewer"]
    E --> F{{"Git-Hooks<br/>pre-commit: gitleaks<br/>pre-push: kein Push auf main"}}
    F --> G["Pull Request gegen main"]
    G --> H["CI (GitHub Actions)<br/>ci + secret-scan"]
    G --> I["Claude-Review<br/>automatisch beim Öffnen"]
    I -. "@claude review<br/>nach neuen Pushes" .-> J["claude.yml"]
    H --> K["Review durch mich → Merge"]
    I --> K
```

## Bausteine

| Ebene | Baustein | Datei | Aufgabe |
|---|---|---|---|
| Claude Code | Skill `naechste-aufgabe` | `.claude/skills/naechste-aufgabe/` | Fester Ablauf: Roadmap → Branch → Plan → Umsetzung → Tests → PR |
| Claude Code | Subagent `tester` | `.claude/agents/tester.md` | Tests schreiben und starten (nur Demo-Daten) |
| Claude Code | Subagent `security-reviewer` | `.claude/agents/security-reviewer.md` | Diff auf Secrets, Token-Lecks, Scraping prüfen |
| Claude Code | Subagent `erklaerer` | `.claude/agents/erklaerer.md` | Änderung zum Lernen erklären |
| Claude Code | Plugins | `~/.claude/settings.json` | feature-dev, ralph-loop, code-review, commit-commands, security-guidance, pyright-lsp, typescript-lsp |
| Claude Code | Hook `protect.py` (PreToolUse) | `.claude/hooks/protect.py` | Blockt Zugriff auf `.env*` (außer `.env.example`), `git commit`/`git push` auf `main`, `--no-verify` und gitleaks-Läufe ohne `--redact` oder über den Arbeitsordner |
| Claude Code | Hook `format.py` (PostToolUse) | `.claude/hooks/format.py` | Formatiert geänderte Dateien mit ruff (backend) bzw. Prettier (frontend), sobald installiert |
| Git lokal | `pre-commit` | `.githooks/pre-commit` | gitleaks prüft die gestagten Änderungen – ein Secret wird gar nicht erst committet |
| Git lokal | `pre-push` | `.githooks/pre-push` | Lehnt Pushes auf `main` ab (Ersatz für Branch Protection, siehe unten) |
| GitHub | CI | `.github/workflows/ci.yml` | Siehe nächster Abschnitt |
| GitHub | Claude-Review | `.github/workflows/claude-review.yml` | Review beim Öffnen eines PRs und bei `ready_for_review`; Drafts übersprungen; max. 15 Turns / 15 min |
| GitHub | `@claude` | `.github/workflows/claude.yml` | Aufgaben per `@claude` in PRs und Issues (z. B. „@claude review“); max. 25 Turns / 30 min; vorerst nur lesend (`contents: read`) |
| GitHub | Dependabot | `.github/dependabot.yml` | Hält die gepinnten Action-Versionen aktuell (wöchentlich) |

Beide Claude-Workflows reagieren nur auf den Repo-Owner (schützt das Pro-Kontingent) und laufen über das **Pro-Abo** (Secret `CLAUDE_CODE_OAUTH_TOKEN`), nicht über die API.

## CI

| Job | Läuft wenn | Prüft |
|---|---|---|
| `detect` | immer | Welche Teile existieren (`backend/pyproject.toml`, `frontend/package.json`, `Dockerfile`) |
| `backend` | `backend/` existiert | `ruff check`, `ruff format --check`, `pyright`, `pytest` |
| `frontend` | `frontend/` existiert | `npm run lint` (ESLint), `npm run format:check` (Prettier), `npm run typecheck` (tsc), `npm test` (Vitest) |
| `docker` | `Dockerfile` existiert | Image baut (ohne Push) |
| `secret-scan` | immer | gitleaks über die **ganze** Git-Historie |
| `ci` | immer | Sammel-Check: rot, wenn einer der Jobs oben fehlschlägt; übersprungene Jobs zählen als bestanden |

Die **required checks** sind später nur `ci` und `secret-scan` – stabil, egal welche Jobs noch dazukommen.

Vertrag für das Projektgerüst: Das Frontend muss die npm-Skripte `lint`, `format:check`, `typecheck` und `test` (einmaliger Lauf, kein Watch-Modus) anbieten; das Backend `ruff`, `pyright` und `pytest` als Dev-Abhängigkeiten in `pyproject.toml`.

Alle Actions sind auf **Commit-SHAs gepinnt** (Version als Kommentar). Ein Tag kann umgehängt werden, ein SHA nicht.

## gitleaks-Regeln

- Immer mit `--redact` – Funde erscheinen nur geschwärzt.
- Nur über Git scannen: `gitleaks git --redact .` (Historie) oder `gitleaks git --pre-commit --staged --redact .` (Hook). **Nie** `gitleaks dir` über den Arbeitsordner – der enthält die echte `.env`.
- `protect.py` blockt beides für Claude.

## Einrichtung (einmalig pro Rechner)

```bash
# 1. Git-Hooks aktivieren
git config core.hooksPath .githooks

# 2. gitleaks installieren – in einem Temp-Ordner, Prüfsumme vor dem Installieren verifizieren
cd "$(mktemp -d)"
V=8.30.1
SHA256=551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb  # wie GITLEAKS_SHA256 in ci.yml
gh release download v$V -R gitleaks/gitleaks -p "gitleaks_${V}_linux_x64.tar.gz"
echo "$SHA256  gitleaks_${V}_linux_x64.tar.gz" | sha256sum -c -
tar -xzf gitleaks_${V}_linux_x64.tar.gz gitleaks && install -m 0755 gitleaks ~/.local/bin/gitleaks
cd -

# 3. Claude-Token fürs Repo (Pro-Abo, einmalig)
claude setup-token
gh secret set CLAUDE_CODE_OAUTH_TOKEN
```

gitleaks-Version und Prüfsumme in `.github/workflows/ci.yml` (`GITLEAKS_VERSION`, `GITLEAKS_SHA256`) und hier gleich halten. Bei einem Update: neuen SHA256 einmal gegen `checksums.txt` des Releases prüfen und an beiden Stellen eintragen. Die Prüfsumme steht fest im Repo, weil eine Datei aus demselben Release ein manipuliertes Release nicht erkennen würde.

## Bekannte Grenzen der lokalen Hooks

Die lokalen Hooks sind ein Sicherheitsnetz gegen Versehen, keine Festung:

- `protect.py` prüft Text, keine echte Shell: Dateinamen wie `prod.env` oder Shell-Globs (`cat .en?`) erkennt es nicht. Erwähnt ein Befehl `.env` nur im Text (z. B. Commit-Message), wird er trotzdem geblockt – lieber einmal zu vorsichtig.
- Bei unlesbarer Eingabe blockt `protect.py` (fail-closed); `format.py` blockt nie.
- `git … --no-verify` umgeht die Git-Hooks. Claude darf das nicht (`protect.py` blockt es), ich selbst könnte es. Endgültig schützt erst die CI (`secret-scan`) und die Branch Protection auf GitHub.
- `claude.yml` ist vorerst nur lesend (`contents: read`): Ohne Branch Protection könnte der Workflow sonst direkt auf `main` schreiben – der lokale `pre-push`-Hook greift im Runner nicht. Umstellung auf `write` ist Teil der Roadmap-Aufgabe „Branch Protection“.
- Die `deny`-Regeln in `.claude/settings.json` nennen nur konkrete Namen (`.env`, `.env.local`, `.env.*.local`, `.env.production`), weil `deny` immer Vorrang hat und ein Muster wie `.env*` auch `.env.example` sperren würde. Alle übrigen Varianten fängt `protect.py` ab.

## Branch Protection

Im kostenlosen Plan gibt es für private Repos keine Branch Protection (GitHub: HTTP 403). **Bis GitHub Pro aktiv ist** (Student Developer Pack beantragt), schützen lokal der `pre-push`-Hook und der Claude-Hook `protect.py` vor Pushes auf `main`. Danach wird eingerichtet:

- Merge nach `main` nur per Pull Request
- Required checks: `ci`, `secret-scan`
- Keine Force-Pushes, kein Löschen von `main`
