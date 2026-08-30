#!/usr/bin/env python3
"""Zwei Fragen: (A) Lassen sich die Artikelseiten in einen Rahmen einbetten?
(B) Gibt es deutsche Feeds, die den Volltext freiwillig mitliefern?"""
import urllib.request, re, xml.etree.ElementTree as ET
from html import unescape
UA="Mozilla/5.0 (compatible; Trainingslog/1.0)"
C="{http://purl.org/rss/1.0/modules/content/}encoded"

def head(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA})
    with urllib.request.urlopen(req,timeout=25) as r:
        h=r.headers
        csp=h.get("Content-Security-Policy","")
        fa=re.search(r"frame-ancestors[^;]*",csp,re.I)
        return h.get("X-Frame-Options","-"), (fa.group(0)[:60] if fa else "-")

print("=== A) Einbetten erlaubt?")
for name,url in [("Tagesschau","https://www.tagesschau.de/"),
                 ("Deutschlandfunk","https://www.deutschlandfunk.de/"),
                 ("taz","https://taz.de/")]:
    try:
        xfo,fa=head(url)
        print(f"  {name:16} X-Frame-Options: {xfo:12} frame-ancestors: {fa}")
    except Exception as e:
        print(f"  {name:16} FEHLER {str(e)[:50]}")

def txt(s): return re.sub(r"\s+"," ",unescape(re.sub(r"<[^>]+>","",s or ""))).strip()
print("\n=== B) Volltext-Feeds?")
for name,url in [("netzpolitik","https://netzpolitik.org/feed/"),
                 ("Riffreporter","https://www.riffreporter.de/rss"),
                 ("Krautreporter","https://krautreporter.de/feed.rss"),
                 ("Wikipedia-Zusammenfassung","https://de.wikipedia.org/api/rest_v1/page/random/summary")]:
    try:
        req=urllib.request.Request(url,headers={"User-Agent":UA})
        with urllib.request.urlopen(req,timeout=25) as r:
            raw=r.read(); hdr=dict(r.headers)
        if url.endswith("summary"):
            import json; d=json.loads(raw)
            print(f"  {name:26} {len(d.get('extract',''))} Zeichen | CORS: {hdr.get('Access-Control-Allow-Origin','-')}")
            print(f"     Beispiel: {d.get('extract','')[:150]}")
            continue
        its=list(ET.fromstring(raw).iter("item"))[:5]
        best=max((len(txt(i.find(C).text)) if i.find(C) is not None else 0) for i in its) if its else 0
        desc=max(len(txt(i.findtext("description"))) for i in its) if its else 0
        print(f"  {name:26} {len(its)} Meldungen | description max {desc:5} | Volltext max {best:6}")
    except Exception as e:
        print(f"  {name:26} FEHLER {str(e)[:55]}")
