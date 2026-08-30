#!/usr/bin/env python3
"""Legt je Wissensthema eine Datei unter wissen/ ab.

Wikipedia steht unter freier Lizenz (CC BY-SA) — anders als bei den
Nachrichtenfeeds darf der Text hier gespeichert und in der App angezeigt
werden, solange Quelle und Lizenz mitlaufen. Deshalb liegt er im Repo und die
Pause funktioniert ohne Netz.

Oberkategorien enthalten oft fast nur Unterkategorien (Kategorie:Geschichte
lieferte zwei Artikel), darum wird eine Ebene tiefer gesammelt.
"""
import json, os, re, sys, time, urllib.parse, urllib.request
from datetime import datetime, timezone

API = "https://de.wikipedia.org/w/api.php"
UA = "Trainingslog/1.0 (https://github.com/lennaxt/Training-log)"
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "wissen")
PER_TOPIC = 40
MIN_LEN = 420          # kuerzere Einleitungen sind Stummel, kein Lesestoff
MAX_LEN = 2600         # laenger sprengt die Pause; wird sauber abgeschnitten
SUBCATS = 14

TOPICS = {
    "physik":      ("Physik",      "Kategorie:Physik"),
    "astronomie":  ("Astronomie",  "Kategorie:Astronomie"),
    "biologie":    ("Biologie",    "Kategorie:Biologie"),
    "medizin":     ("Medizin",     "Kategorie:Medizin"),
    "geschichte":  ("Geschichte",  "Kategorie:Geschichte"),
    "philosophie": ("Philosophie", "Kategorie:Philosophie"),
    "technik":     ("Technik",     "Kategorie:Technik"),
    "psychologie": ("Psychologie", "Kategorie:Psychologie"),
}


def api(**params):
    params.update(action="query", format="json", formatversion="2")
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params),
                                 headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def tidy(s):
    s = (s or "").replace(" ", " ")
    # Formel-Artikel hinterlassen im Klartext Bloecke aus Leerraum und
    # Einzelbuchstaben - solche Artikel sind als Lesestoff unbrauchbar.
    if re.search(r"\n\s{4,}\S", s) or re.search(r"[ \t]{6,}", s):
        return ""
    s = re.sub(r"\s*\n\s*", "\n", s).strip()
    s = re.sub(r"[ \t]{2,}", " ", s)
    return s


def cut(s):
    if len(s) <= MAX_LEN:
        return s
    teil = s[:MAX_LEN]
    p = max(teil.rfind(". "), teil.rfind(".\n"))
    return (teil[:p + 1] if p > MAX_LEN * .6 else teil.rstrip()) + " …"


def kategorien(wurzel):
    """Wurzel plus eine Ebene Unterkategorien."""
    try:
        d = api(list="categorymembers", cmtitle=wurzel, cmtype="subcat", cmlimit=str(SUBCATS))
        return [wurzel] + [m["title"] for m in d.get("query", {}).get("categorymembers", [])]
    except Exception:
        return [wurzel]


def artikel(kat, limit=24):
    try:
        d = api(generator="categorymembers", gcmtitle=kat, gcmlimit=str(limit),
                gcmnamespace="0", prop="extracts", exintro="1", explaintext="1")
    except Exception:
        return []
    out = []
    for p in d.get("query", {}).get("pages", []):
        t = tidy(p.get("extract"))
        if len(t) < MIN_LEN:
            continue
        out.append({"t": p["title"], "s": cut(t),
                    "u": "https://de.wikipedia.org/wiki/" + urllib.parse.quote(p["title"].replace(" ", "_")),
                    "q": "Wikipedia"})
    return out


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    ok = 0
    for key, (name, wurzel) in TOPICS.items():
        gefunden, gesehen = [], set()
        for kat in kategorien(wurzel):
            for a in artikel(kat):
                if a["t"] in gesehen:
                    continue
                gesehen.add(a["t"])
                gefunden.append(a)
            if len(gefunden) >= PER_TOPIC:
                break
            time.sleep(.2)
        if not gefunden:
            print(f"{key:13} FEHLER, alter Stand bleibt", file=sys.stderr)
            continue
        gefunden.sort(key=lambda a: a["t"])
        with open(os.path.join(OUT_DIR, key + ".json"), "w", encoding="utf-8") as f:
            json.dump({"name": name,
                       "lizenz": "Wikipedia, CC BY-SA 4.0",
                       "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                       "items": gefunden[:PER_TOPIC]}, f, ensure_ascii=False, indent=1)
            f.write("\n")
        ok += 1
        ln = sorted(len(a["s"]) for a in gefunden[:PER_TOPIC])
        print(f"{key:13} {len(gefunden[:PER_TOPIC]):3} Artikel | Zeichen: min {ln[0]:5} med {ln[len(ln)//2]:5} max {ln[-1]:5}")
    if not ok:
        print("Kein einziges Thema gefuellt.", file=sys.stderr)
        return 1
    print(f"\n{ok}/{len(TOPICS)} Themen aktualisiert.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
