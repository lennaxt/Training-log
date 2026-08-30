#!/usr/bin/env python3
"""Legt je Thema eine Datei unter news/ ab, neben index.html.

GitHub Pages liefert sie von derselben Herkunft wie die App aus — damit braucht
der Browser keinen fremden Dienst und laeuft nicht in CORS.

Die Themen kommen aus den Ressort-Feeds der Quellen, nicht aus eigener
Einsortierung: keiner der drei Hauptfeeds fuehrt <category>, dafuer haben alle
drei eigene Ressort-Adressen. Was hier waechst, ist diese Tabelle — nicht der
Code darunter.
"""
import json, os, re, sys, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape

TOPICS = {
    "inland": ("Inland", [
        ("Tagesschau", "https://www.tagesschau.de/inland/index~rss2.xml"),
        ("Deutschlandfunk", "https://www.deutschlandfunk.de/politikportal-100.rss"),
        ("taz", "https://taz.de/Politik/!p4615;rss/")]),
    "ausland": ("Ausland", [
        ("Tagesschau", "https://www.tagesschau.de/ausland/index~rss2.xml")]),
    "wirtschaft": ("Wirtschaft", [
        ("Tagesschau", "https://www.tagesschau.de/wirtschaft/index~rss2.xml"),
        ("Deutschlandfunk", "https://www.deutschlandfunk.de/wirtschaft-106.rss")]),
    "wissen": ("Wissen", [
        ("Tagesschau", "https://www.tagesschau.de/wissen/index~rss2.xml")]),
    "umwelt": ("Umwelt", [
        ("taz", "https://taz.de/Oeko/!p4616;rss/")]),
    "gesellschaft": ("Gesellschaft", [
        ("taz", "https://taz.de/Gesellschaft/!p4617;rss/")]),
    "kultur": ("Kultur", [
        ("taz", "https://taz.de/Kultur/!p4618;rss/")]),
    "sport": ("Sport", [
        ("taz", "https://taz.de/Sport/!p4619;rss/")]),
}
PER_TOPIC = 24
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "news")
UA = "Trainingslog-Newsbot/1.0 (+https://github.com/lennaxt/Training-log)"


def clean(s, limit):
    s = re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", "", s or ""))).strip()
    return s[:limit].rstrip() + "…" if len(s) > limit else s


def when(item):
    # taz laesst den Wochentag weg, die anderen nicht - parsedate kommt mit beidem klar.
    raw = item.findtext("pubDate")
    try:
        return parsedate_to_datetime(raw).astimezone(timezone.utc)
    except Exception:
        return None


def items_of(raw, source):
    out = []
    for it in ET.fromstring(raw).iter("item"):
        title = clean(it.findtext("title"), 140)
        if not title:
            continue
        d = when(it)
        out.append({"t": title,
                    "s": clean(it.findtext("description"), 320),
                    "u": (it.findtext("link") or "").strip(),
                    "q": source,
                    "d": d.isoformat(timespec="seconds") if d else None})
    return out


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    ok = 0
    for key, (name, feeds) in TOPICS.items():
        path = os.path.join(OUT_DIR, key + ".json")
        pool, broken = [], []
        for source, url in feeds:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=25) as r:
                    pool += items_of(r.read(), source)
            except Exception as e:
                broken.append(f"{source} ({e})")

        if not pool:
            print(f"{key:13} FEHLER, alter Stand bleibt: {'; '.join(broken)}", file=sys.stderr)
            continue

        # Neueste zuerst; Meldungen ohne Datum ans Ende statt raus.
        pool.sort(key=lambda i: i["d"] or "", reverse=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"name": name,
                       "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                       "items": pool[:PER_TOPIC]}, f, ensure_ascii=False, indent=1)
            f.write("\n")
        ok += 1
        note = f"  (kaputt: {'; '.join(broken)})" if broken else ""
        print(f"{key:13} {min(len(pool), PER_TOPIC):3} Meldungen aus {len(feeds) - len(broken)}/{len(feeds)} Feeds{note}")

    if not ok:
        print("Kein einziges Thema konnte gefuellt werden.", file=sys.stderr)
        return 1
    print(f"\n{ok}/{len(TOPICS)} Themen aktualisiert.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
