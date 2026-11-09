"""Phase-0-Test: Prüft, ob die Moodle-API des TH-Lernraums erreichbar ist.

Holt einen Token wie die offizielle Moodle-App (Benutzername + Passwort werden
nicht angezeigt und nicht gespeichert) und ruft danach einige Funktionen auf.
Optional: Token in .env speichern (Rechte 600).
"""
import getpass
import json
import os
import time
import urllib.parse
import urllib.request

BASIS = os.environ.get("MOODLE_URL", "https://lernraum.th-luebeck.de")


def hole_token() -> str:
    token = os.environ.get("MOODLE_TOKEN")
    if token:
        print("✔ Token aus Umgebungsvariable MOODLE_TOKEN")
        return token
    benutzer = input("TH-Benutzername: ")
    passwort = getpass.getpass("Passwort (wird nicht angezeigt): ")
    daten = urllib.parse.urlencode(
        {"username": benutzer, "password": passwort, "service": "moodle_mobile_app"}
    ).encode()
    with urllib.request.urlopen(BASIS + "/login/token.php", data=daten) as r:
        antwort = json.load(r)
    del passwort
    if "token" not in antwort:
        raise SystemExit(f"✘ Kein Token: {antwort.get('errorcode')} – {antwort.get('error')}")
    print("✔ Token erhalten")
    if input("Token in .env speichern? [j/N] ").strip().lower() == "j":
        with open(".env", "a", encoding="utf-8") as f:
            f.write(f"MOODLE_URL={BASIS}\nMOODLE_TOKEN={antwort['token']}\n")
        os.chmod(".env", 0o600)
        print("✔ In .env gespeichert (nur für dich lesbar, steht in .gitignore)")
    return antwort["token"]


TOKEN = hole_token()


def call(funktion, **params):
    params.update(wstoken=TOKEN, wsfunction=funktion, moodlewsrestformat="json")
    url = BASIS + "/webservice/rest/server.php?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url) as r:
        d = json.load(r)
    if isinstance(d, dict) and "exception" in d:
        raise RuntimeError(f"{funktion}: {d.get('errorcode')} – {d.get('message')}")
    return d


info = call("core_webservice_get_site_info")
print(f"✔ Verbunden als {info['fullname']} – Moodle {info.get('release', '?')}")

kurse = call("core_enrol_get_users_courses", userid=info["userid"])
print(f"✔ {len(kurse)} Kurse gefunden")

if kurse:
    inhalt = call("core_course_get_contents", courseid=kurse[0]["id"])
    dateien = sum(len(m.get("contents", [])) for s in inhalt for m in s.get("modules", []))
    print(f"✔ Kurs '{kurse[0]['shortname']}': {len(inhalt)} Abschnitte, {dateien} Dateien")

jetzt = int(time.time())
termine = call("core_calendar_get_action_events_by_timesort",
               timesortfrom=jetzt, timesortto=jetzt + 30 * 86400)
print(f"✔ {len(termine.get('events', []))} anstehende Termine (30 Tage)")

print("\nErgebnis: GO")
