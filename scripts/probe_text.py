#!/usr/bin/env python3
"""Wie viel Text geben die Feeds ueber den Teaser hinaus her? Danach loeschen."""
import urllib.request, re, xml.etree.ElementTree as ET
from html import unescape
UA="Trainingslog-Newsbot/1.0 (+https://github.com/lennaxt/Training-log)"
C="{http://purl.org/rss/1.0/modules/content/}encoded"
FEEDS=[("Tagesschau","https://www.tagesschau.de/inland/index~rss2.xml"),
       ("Tagesschau-Wissen","https://www.tagesschau.de/wissen/index~rss2.xml"),
       ("Deutschlandfunk","https://www.deutschlandfunk.de/politikportal-100.rss"),
       ("taz","https://taz.de/Politik/!p4615;rss/")]
def txt(s): return re.sub(r"\s+"," ",unescape(re.sub(r"<[^>]+>","",s or ""))).strip()
for name,url in FEEDS:
    try:
        req=urllib.request.Request(url,headers={"User-Agent":UA})
        with urllib.request.urlopen(req,timeout=25) as r: raw=r.read()
        its=list(ET.fromstring(raw).iter("item"))[:8]
        print(f"\n=== {name} ({len(its)} geprueft)")
        for i in its[:4]:
            d=len(txt(i.findtext("description")))
            c=txt(i.find(C).text) if i.find(C) is not None else ""
            print(f"  description {d:5} | content:encoded {len(c):6} | {txt(i.findtext('title'))[:40]}")
        if its and its[0].find(C) is not None:
            print("  Anfang content:encoded:", txt(its[0].find(C).text)[:220])
    except Exception as e:
        print(f"\n=== {name} FEHLER {e}")
