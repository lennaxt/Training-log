#!/usr/bin/env python3
"""Legt je Wissensthema eine Datei unter wissen/ ab.

Wikipedia steht unter freier Lizenz (CC BY-SA) — anders als bei den
Nachrichtenfeeds darf der Text hier gespeichert und in der App angezeigt
werden, solange Quelle und Lizenz mitlaufen. Deshalb liegt er im Repo und die
Pause funktioniert ohne Netz.

Oberkategorien enthalten oft fast nur Unterkategorien (Kategorie:Geschichte
lieferte zwei Artikel), darum wird eine Ebene tiefer gesammelt.
"""
import json, os, random, re, sys, time, urllib.parse, urllib.request
from datetime import datetime, timezone

API = "https://de.wikipedia.org/w/api.php"
UA = "Trainingslog/1.0 (https://github.com/lennaxt/Training-log)"
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "wissen")
PER_TOPIC = 40
MIN_LEN = 420          # kuerzere Einleitungen sind Stummel, kein Lesestoff
MAX_LEN = 2600         # laenger sprengt die Pause; wird sauber abgeschnitten
SUBCATS = 14
PROBE = 140          # so viele Titel werden auf Textlaenge geprueft

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


def titel(kat):
    """Nur die Namen, das ist billig und liefert bis zu 500 auf einmal.
    Getrennt vom Textabruf, weil der auf 20 Seiten je Anfrage begrenzt ist —
    zusammen ergaebe das sonst immer nur den Anfang des Alphabets."""
    try:
        d = api(list="categorymembers", cmtitle=kat, cmnamespace="0", cmlimit="500")
        return [m["title"] for m in d.get("query", {}).get("categorymembers", [])]
    except Exception:
        return []


def texte(namen):
    out = []
    for i in range(0, len(namen), 20):
        teil = namen[i:i + 20]
        try:
            d = api(titles="|".join(teil), prop="extracts",
                    exintro="1", explaintext="1", exlimit="20")
        except Exception:
            continue
        for pg in d.get("query", {}).get("pages", []):
            # Verzeichnisartikel sind zum Nachschlagen da, nicht zum Lesen.
            if re.match(r"^(Liste|Kategorie|Portal|Datei|Wikipedia)\b", pg["title"]):
                continue
            t = tidy(pg.get("extract"))
            if len(t) < MIN_LEN:
                continue
            out.append({"t": pg["title"], "s": cut(t),
                        "u": "https://de.wikipedia.org/wiki/" + urllib.parse.quote(pg["title"].replace(" ", "_")),
                        "q": "Wikipedia"})
        time.sleep(.2)
    return out


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    ok = 0
    for key, (name, wurzel) in TOPICS.items():
        kandidaten = []
        for kat in kategorien(wurzel):
            kandidaten += titel(kat)
        kandidaten = list(dict.fromkeys(kandidaten))
        random.shuffle(kandidaten)
        gefunden = texte(kandidaten[:PROBE])
        if not gefunden:
            print(f"{key:13} FEHLER, alter Stand bleibt", file=sys.stderr)
            continue
        random.shuffle(gefunden)
        gefunden = sorted(gefunden[:PER_TOPIC], key=lambda a: a["t"])
        with open(os.path.join(OUT_DIR, key + ".json"), "w", encoding="utf-8") as f:
            json.dump({"name": name,
                       "lizenz": "Wikipedia, CC BY-SA 4.0",
                       "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                       "items": gefunden}, f, ensure_ascii=False, indent=1)
            f.write("\n")
        ok += 1
        ln = sorted(len(a["s"]) for a in gefunden)
        abc = len({a["t"][0].upper() for a in gefunden})
        print(f"{key:13} {len(gefunden):3} Artikel aus {len(kandidaten):5} Kandidaten | "
              f"{abc:2} Anfangsbuchstaben | Zeichen med {ln[len(ln)//2]:5}")
    if not ok:
        print("Kein einziges Thema gefuellt.", file=sys.stderr)
        return 1
    print(f"\n{ok}/{len(TOPICS)} Themen aktualisiert.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
