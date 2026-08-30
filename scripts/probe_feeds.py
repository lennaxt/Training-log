#!/usr/bin/env python3
"""Einmaliger Erkundungslauf: welche Ressort-Feeds existieren, und tragen die
Meldungen der Hauptfeeds schon eine Kategorie? Danach wieder loeschen."""
import urllib.request, xml.etree.ElementTree as ET
from collections import Counter

UA = "Trainingslog-Newsbot/1.0 (+https://github.com/lennaxt/Training-log)"
MAIN = {
    "tagesschau": "https://www.tagesschau.de/xml/rss2/",
    "dlf": "https://www.deutschlandfunk.de/nachrichten-100.rss",
    "taz": "https://taz.de/!p4608;rss/",
}
CANDIDATES = [
    "https://www.tagesschau.de/inland/index~rss2.xml",
    "https://www.tagesschau.de/ausland/index~rss2.xml",
    "https://www.tagesschau.de/wirtschaft/index~rss2.xml",
    "https://www.tagesschau.de/wissen/index~rss2.xml",
    "https://www.tagesschau.de/xml/rss2_ressort_inland/",
    "https://www.deutschlandfunk.de/politikportal-100.rss",
    "https://www.deutschlandfunk.de/wirtschaft-106.rss",
    "https://www.deutschlandfunk.de/wissenschaft-106.rss",
    "https://www.deutschlandfunk.de/kultur-106.rss",
    "https://www.deutschlandfunk.de/sport-106.rss",
    "https://www.deutschlandfunk.de/europa-108.rss",
    "https://taz.de/Politik/!p4615;rss/",
    "https://taz.de/Oeko/!p4616;rss/",
    "https://taz.de/Gesellschaft/!p4617;rss/",
    "https://taz.de/Kultur/!p4618;rss/",
    "https://taz.de/Sport/!p4619;rss/",
]

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()

print("=" * 60)
print("A) Tragen die Hauptfeeds Kategorien und Datum?")
for key, url in MAIN.items():
    try:
        items = list(ET.fromstring(get(url)).iter("item"))
        cats = Counter(c.text.strip() for i in items for c in i.findall("category") if c.text)
        has_date = sum(1 for i in items if i.findtext("pubDate"))
        print(f"\n{key}: {len(items)} Meldungen, {has_date} mit pubDate")
        print(f"  Beispiel-Datum: {items[0].findtext('pubDate') if items else '-'}")
        print(f"  Kategorien ({len(cats)} verschiedene): {dict(cats.most_common(12)) or 'KEINE'}")
        print(f"  Felder je Meldung: {sorted({c.tag for c in items[0]})}" if items else "")
    except Exception as e:
        print(f"\n{key}: FEHLER {e}")

print()
print("=" * 60)
print("B) Welche Ressort-Adressen existieren?")
for url in CANDIDATES:
    try:
        n = len(list(ET.fromstring(get(url)).iter("item")))
        print(f"  {'OK ' if n else 'LEER'} {n:3}  {url}")
    except Exception as e:
        print(f"  FEHLER   {str(e)[:45]:45} {url}")
