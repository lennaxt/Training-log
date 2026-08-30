#!/usr/bin/env python3
"""(A) Erlaubt Wikipedia den Zugriff aus dem Browser? (B) Wie hole ich Artikel
je Thema? (C) Wie lang ist die Einleitung wirklich?"""
import json, urllib.request, urllib.parse
UA = "Trainingslog/1.0 (https://github.com/lennaxt/Training-log)"
API = "https://de.wikipedia.org/w/api.php"

def get(url, origin=None):
    h = {"User-Agent": UA}
    if origin: h["Origin"] = origin
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.headers, r.read()

print("=== A) CORS, diesmal MIT Origin-Kopf")
for path in ["/api/rest_v1/page/random/summary", "/w/api.php?action=query&format=json&origin=*&meta=siteinfo"]:
    try:
        h, _ = get("https://de.wikipedia.org" + path, origin="https://lennaxt.github.io")
        print(f"  {path[:44]:46} ACAO: {h.get('Access-Control-Allow-Origin','FEHLT')}")
    except Exception as e:
        print(f"  {path[:44]:46} FEHLER {str(e)[:40]}")

print("\n=== B+C) Artikel je Thema, Laenge der Einleitung")
THEMEN = {"Physik":"Kategorie:Physik", "Geschichte":"Kategorie:Geschichte",
          "Biologie":"Kategorie:Biologie", "Astronomie":"Kategorie:Astronomie",
          "Philosophie":"Kategorie:Philosophie", "Technik":"Kategorie:Technik"}
for name, kat in THEMEN.items():
    try:
        q = urllib.parse.urlencode({"action":"query","format":"json","origin":"*",
            "generator":"categorymembers","gcmtitle":kat,"gcmlimit":"12","gcmnamespace":"0",
            "prop":"extracts","exintro":"1","explaintext":"1"})
        _, raw = get(API + "?" + q)
        pages = json.loads(raw).get("query",{}).get("pages",{})
        arts = [p for p in pages.values() if p.get("extract")]
        ln = sorted(len(p["extract"]) for p in arts)
        med = ln[len(ln)//2] if ln else 0
        print(f"  {name:12} {len(arts):3} Artikel | Einleitung: min {ln[0] if ln else 0:5} med {med:5} max {ln[-1] if ln else 0:6}")
        if arts:
            a = max(arts, key=lambda p: len(p["extract"]))
            print(f"     '{a['title']}': {a['extract'][:180]}...")
    except Exception as e:
        print(f"  {name:12} FEHLER {str(e)[:60]}")
